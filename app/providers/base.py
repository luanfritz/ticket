from abc import ABC, abstractmethod
from datetime import date

from app.models import FlightOption


class FlightProvider(ABC):
    @abstractmethod
    async def search(self, origin: str, destination: str, travel_date: date) -> list[FlightOption]:
        raise NotImplementedError
