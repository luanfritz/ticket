import os
from datetime import date, datetime
from typing import Any

import httpx

from app.models import FlightOption
from app.providers.base import FlightProvider


class AmadeusFlightProvider(FlightProvider):
    """Provider opcional com integração real na API da Amadeus."""

    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    flight_offers_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self) -> None:
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")

    async def search(self, origin: str, destination: str, travel_date: date) -> list[FlightOption]:
        if not (self.api_key and self.api_secret):
            return []

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                token = await self._fetch_access_token(client)
                response = await client.get(
                    self.flight_offers_url,
                    params={
                        "originLocationCode": origin,
                        "destinationLocationCode": destination,
                        "departureDate": travel_date.isoformat(),
                        "adults": 1,
                        "max": 20,
                        "currencyCode": "BRL",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
            except (httpx.HTTPError, ValueError):
                return []

        return self._map_offers_to_options(response.json(), origin, destination)

    async def _fetch_access_token(self, client: httpx.AsyncClient) -> str:
        response = await client.post(
            self.auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if not token:
            raise ValueError("Amadeus auth response without access_token")
        return token

    def _map_offers_to_options(self, payload: dict[str, Any], origin: str, destination: str) -> list[FlightOption]:
        options: list[FlightOption] = []

        for offer in payload.get("data", []):
            itineraries = offer.get("itineraries") or []
            if not itineraries:
                continue

            itinerary = itineraries[0]
            segments = itinerary.get("segments") or []
            if not segments:
                continue

            departure_at = self._parse_dt(segments[0].get("departure", {}).get("at"))
            arrival_at = self._parse_dt(segments[-1].get("arrival", {}).get("at"))
            if not (departure_at and arrival_at):
                continue

            price = offer.get("price", {})
            total_price = self._parse_float(price.get("total"))
            if total_price <= 0:
                continue

            taxes = self._extract_taxes(price)
            option = FlightOption(
                id=str(offer.get("id") or f"AMADEUS-{origin}-{destination}-{departure_at.isoformat()}"),
                origin=segments[0].get("departure", {}).get("iataCode", origin),
                destination=segments[-1].get("arrival", {}).get("iataCode", destination),
                departure_at=departure_at,
                arrival_at=arrival_at,
                airline=self._extract_airline(offer, segments),
                connections=max(len(segments) - 1, 0),
                cash_price_brl=total_price,
                taxes_brl=taxes,
                source="amadeus",
            )
            options.append(option)

        return options

    def _extract_airline(self, offer: dict[str, Any], segments: list[dict[str, Any]]) -> str:
        validating = offer.get("validatingAirlineCodes") or []
        if validating:
            return str(validating[0])

        carrier_codes = [segment.get("carrierCode") for segment in segments if segment.get("carrierCode")]
        unique_codes = list(dict.fromkeys(carrier_codes))
        return "+".join(unique_codes) if unique_codes else "UNKNOWN"

    def _extract_taxes(self, price: dict[str, Any]) -> float:
        fees = price.get("fees") or []
        total_fees = sum(self._parse_float(fee.get("amount")) for fee in fees)
        if total_fees > 0:
            return total_fees

        grand_total = self._parse_float(price.get("grandTotal"))
        total = self._parse_float(price.get("total"))
        return max(grand_total - total, 0)

    def _parse_dt(self, value: Any) -> datetime | None:
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _parse_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
