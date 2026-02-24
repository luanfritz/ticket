from datetime import date, datetime, timedelta

from app.models import FlightOption
from app.providers.base import FlightProvider


class MockFlightProvider(FlightProvider):
    async def search(self, origin: str, destination: str, travel_date: date) -> list[FlightOption]:
        base_departure = datetime.combine(travel_date, datetime.min.time()).replace(hour=8)
        return [
            FlightOption(
                id=f"MK-{origin}{destination}-1",
                origin=origin,
                destination=destination,
                departure_at=base_departure,
                arrival_at=base_departure + timedelta(hours=2, minutes=30),
                airline="Azul",
                connections=0,
                cash_price_brl=780.0,
                miles_price=42000,
                taxes_brl=39.90,
                source="mock",
            ),
            FlightOption(
                id=f"MK-{origin}{destination}-2",
                origin=origin,
                destination=destination,
                departure_at=base_departure.replace(hour=10),
                arrival_at=base_departure.replace(hour=15),
                airline="LATAM",
                connections=1,
                cash_price_brl=640.0,
                miles_price=47000,
                taxes_brl=49.90,
                source="mock",
            ),
            FlightOption(
                id=f"MK-{origin}{destination}-3",
                origin=origin,
                destination=destination,
                departure_at=base_departure.replace(hour=13),
                arrival_at=base_departure.replace(hour=20),
                airline="GOL",
                connections=2,
                cash_price_brl=520.0,
                miles_price=60000,
                taxes_brl=54.90,
                source="mock",
            ),
        ]
