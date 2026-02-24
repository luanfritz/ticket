import os
from datetime import date

import httpx

from app.models import FlightOption
from app.providers.base import FlightProvider


class AmadeusFlightProvider(FlightProvider):
    """Provider opcional. Retorna lista vazia sem credenciais válidas."""

    def __init__(self) -> None:
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")

    async def search(self, origin: str, destination: str, travel_date: date) -> list[FlightOption]:
        if not (self.api_key and self.api_secret):
            return []

        # Stub defensivo: ponto de extensão para integração real.
        # Mantido sem chamada externa para garantir execução local sem segredos.
        async with httpx.AsyncClient(timeout=10) as client:
            _ = client
        return []
