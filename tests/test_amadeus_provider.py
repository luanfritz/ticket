import asyncio
from datetime import date

import httpx

from app.providers.amadeus_provider import AmadeusFlightProvider


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(self.status_code),
            )

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, data=None, headers=None):
        self.calls.append(("POST", url, data, headers))
        return FakeResponse({"access_token": "token-123"})

    async def get(self, url, params=None, headers=None):
        self.calls.append(("GET", url, params, headers))
        return FakeResponse(
            {
                "data": [
                    {
                        "id": "1",
                        "validatingAirlineCodes": ["LA"],
                        "itineraries": [
                            {
                                "segments": [
                                    {
                                        "departure": {"iataCode": "GRU", "at": "2026-03-10T09:00:00"},
                                        "arrival": {"iataCode": "BSB", "at": "2026-03-10T10:30:00"},
                                        "carrierCode": "LA",
                                    },
                                    {
                                        "departure": {"iataCode": "BSB", "at": "2026-03-10T12:00:00"},
                                        "arrival": {"iataCode": "REC", "at": "2026-03-10T14:30:00"},
                                        "carrierCode": "LA",
                                    },
                                ]
                            }
                        ],
                        "price": {"total": "1234.56", "fees": [{"amount": "45.67"}]},
                    }
                ]
            }
        )


def test_amadeus_provider_calls_api_and_maps_offer(monkeypatch):
    monkeypatch.setenv("AMADEUS_API_KEY", "key")
    monkeypatch.setenv("AMADEUS_API_SECRET", "secret")
    monkeypatch.setattr("app.providers.amadeus_provider.httpx.AsyncClient", FakeAsyncClient)

    provider = AmadeusFlightProvider()
    options = asyncio.run(provider.search("GRU", "REC", date(2026, 3, 10)))

    assert len(options) == 1
    option = options[0]
    assert option.id == "1"
    assert option.origin == "GRU"
    assert option.destination == "REC"
    assert option.connections == 1
    assert option.cash_price_brl == 1234.56
    assert option.taxes_brl == 45.67
    assert option.airline == "LA"
    assert option.source == "amadeus"


def test_amadeus_provider_returns_empty_on_http_error(monkeypatch):
    class BrokenClient(FakeAsyncClient):
        async def post(self, url, data=None, headers=None):
            return FakeResponse({}, status_code=401)

    monkeypatch.setenv("AMADEUS_API_KEY", "key")
    monkeypatch.setenv("AMADEUS_API_SECRET", "secret")
    monkeypatch.setattr("app.providers.amadeus_provider.httpx.AsyncClient", BrokenClient)

    provider = AmadeusFlightProvider()
    options = asyncio.run(provider.search("GRU", "REC", date(2026, 3, 10)))

    assert options == []
