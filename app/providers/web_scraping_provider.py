import asyncio
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable

import httpx

from app.models import FlightOption
from app.providers.base import FlightProvider


@dataclass(frozen=True)
class ScrapingSource:
    name: str
    search_url_template: str


class WebScrapingFlightProvider(FlightProvider):
    """Best-effort scraping provider for metasearch websites.

    Many fare websites render data dynamically and can block bots aggressively,
    so this provider is intentionally resilient and optional.
    """

    SOURCES: tuple[ScrapingSource, ...] = (
        ScrapingSource("google_flights", "https://www.google.com/travel/flights?hl=pt-BR#flt={origin}.{destination}.{date}"),
        ScrapingSource("kayak", "https://www.kayak.com.br/flights/{origin}-{destination}/{date}?sort=bestflight_a"),
        ScrapingSource("skyscanner", "https://www.skyscanner.com.br/transporte/voos/{origin}/{destination}/{date}"),
        ScrapingSource("decolar", "https://www.decolar.com/shop/flights/results/oneway/{origin}/{destination}/{date}/1/0/0/NA/NA/NA/NA/NA?from=SB"),
        ScrapingSource("viajanet", "https://www.viajanet.com.br/passagens-aereas/{origin}-{destination}?departureDate={date}"),
        ScrapingSource("123milhas", "https://123milhas.com/v2/passagens-aereas/{origin}/{destination}/{date}"),
        ScrapingSource("latam", "https://www.latamairlines.com/br/pt/ofertas-voos?from={origin}&to={destination}&outbound={date}"),
        ScrapingSource("gol", "https://www.voegol.com.br/compra/selecao-de-voo?trecho=OW&de={origin}&para={destination}&ida={date}"),
        ScrapingSource("azul", "https://www.voeazul.com.br/br/pt/home/selecao-voo?origem={origin}&destino={destination}&dataIda={date}"),
    )

    def __init__(self) -> None:
        self.enabled = os.getenv("ENABLE_WEB_SCRAPING", "false").lower() == "true"
        self.timeout_s = float(os.getenv("WEB_SCRAPING_TIMEOUT_SECONDS", "3.0"))
        self.max_sources = int(os.getenv("WEB_SCRAPING_MAX_SOURCES", str(len(self.SOURCES))))
        self.user_agent = os.getenv(
            "WEB_SCRAPING_USER_AGENT",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        )

    async def search(self, origin: str, destination: str, travel_date: date) -> list[FlightOption]:
        if not self.enabled:
            return []

        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        async with httpx.AsyncClient(timeout=self.timeout_s, follow_redirects=True, headers=headers) as client:
            tasks = [
                self._fetch_and_parse(client, source, origin, destination, travel_date)
                for source in self.SOURCES[: self.max_sources]
            ]
            batches = await asyncio.gather(*tasks, return_exceptions=True)

        options: list[FlightOption] = []
        for batch in batches:
            if isinstance(batch, Exception):
                continue
            options.extend(batch)

        return self._deduplicate(options)

    async def _fetch_and_parse(
        self,
        client: httpx.AsyncClient,
        source: ScrapingSource,
        origin: str,
        destination: str,
        travel_date: date,
    ) -> list[FlightOption]:
        url = source.search_url_template.format(origin=origin, destination=destination, date=travel_date.isoformat())

        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            return []

        prices = self._extract_prices_brl(response.text)
        if not prices:
            return []

        results: list[FlightOption] = []
        departure = datetime.combine(travel_date, time(hour=7))

        for index, price in enumerate(prices[:3], start=1):
            results.append(
                FlightOption(
                    id=f"SCRAPE-{source.name}-{origin}{destination}-{travel_date.isoformat()}-{index}",
                    origin=origin,
                    destination=destination,
                    departure_at=departure + timedelta(hours=index),
                    arrival_at=departure + timedelta(hours=index + 2, minutes=35),
                    airline="MIXED",
                    connections=1,
                    cash_price_brl=price,
                    taxes_brl=0,
                    source=f"scraping:{source.name}",
                )
            )

        return results

    def _extract_prices_brl(self, text: str) -> list[float]:
        candidates: list[float] = []

        for pattern in (
            r"R\$\s*([0-9]{2,5}(?:\.[0-9]{3})*(?:,[0-9]{2})?)",
            r'"price"\s*:\s*"?([0-9]{2,5}(?:\.[0-9]{3})*(?:,[0-9]{2})?)"?',
            r'"totalPrice"\s*:\s*"?([0-9]{2,5}(?:\.[0-9]{3})*(?:,[0-9]{2})?)"?',
        ):
            for raw in re.findall(pattern, text):
                value = self._parse_brl(raw)
                if value and 50 <= value <= 25000:
                    candidates.append(value)

        unique = sorted(set(candidates))
        return unique[:5]

    def _parse_brl(self, raw: str) -> float | None:
        normalized = raw.replace(".", "").replace(",", ".")
        try:
            return round(float(normalized), 2)
        except ValueError:
            return None

    def _deduplicate(self, options: Iterable[FlightOption]) -> list[FlightOption]:
        seen: set[tuple[str, str, str, float]] = set()
        output: list[FlightOption] = []
        for option in options:
            key = (option.source, option.origin, option.destination, option.cash_price_brl)
            if key in seen:
                continue
            seen.add(key)
            output.append(option)
        return output
