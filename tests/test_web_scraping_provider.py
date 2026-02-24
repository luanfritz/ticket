import asyncio
from datetime import date

from app.providers.web_scraping_provider import WebScrapingFlightProvider


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.payload = kwargs.pop("payload")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url):
        return FakeResponse(self.payload)


def test_web_scraping_provider_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_WEB_SCRAPING", raising=False)

    provider = WebScrapingFlightProvider()

    assert provider.enabled is False


def test_web_scraping_provider_extracts_prices(monkeypatch):
    monkeypatch.setenv("ENABLE_WEB_SCRAPING", "true")
    monkeypatch.setenv("WEB_SCRAPING_MAX_SOURCES", "1")

    html = '<html><body>Oferta por R$ 1.299,90 e fallback "price":"899,50"</body></html>'

    def fake_async_client(*args, **kwargs):
        kwargs["payload"] = html
        return FakeClient(*args, **kwargs)

    monkeypatch.setattr("app.providers.web_scraping_provider.httpx.AsyncClient", fake_async_client)

    provider = WebScrapingFlightProvider()
    options = asyncio.run(provider.search("GRU", "REC", date(2026, 4, 5)))

    assert len(options) == 2
    assert options[0].source.startswith("scraping:")
    assert min(option.cash_price_brl for option in options) == 899.5
