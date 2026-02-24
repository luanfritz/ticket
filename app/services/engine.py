from datetime import date

from app.models import (
    FlightOption,
    FlightSearchRequest,
    FlightSearchResponse,
    RankedFlightOption,
    RiskLevel,
    StrategyRecommendation,
)
from app.providers.amadeus_provider import AmadeusFlightProvider
from app.providers.mock_provider import MockFlightProvider
from app.providers.web_scraping_provider import WebScrapingFlightProvider
from app.services.miles import is_miles_good_deal
from app.services.promotions import match_promotions
from app.services.scoring import score_option, total_minutes, value_per_mile


class FlightEngine:
    def __init__(self) -> None:
        self.providers = [AmadeusFlightProvider(), WebScrapingFlightProvider(), MockFlightProvider()]
        self.min_connection_minutes = 90
        self.max_connection_minutes = 360

    async def search(self, request: FlightSearchRequest) -> FlightSearchResponse:
        options: list[FlightOption] = []
        for provider in self.providers:
            options.extend(await provider.search(request.origin, request.destination, request.date))

        ranked = sorted(
            [self._build_ranked_option(option) for option in options],
            key=lambda item: item.score,
        )

        direct_best_price = min((item.option.cash_price_brl for item in ranked), default=float("inf"))
        split_suggestions = await self._split_ticket_suggestions(
            request.origin, request.destination, request.date, direct_best_price
        )

        best_cash = ranked[0] if ranked else None
        best_miles = self._best_miles_option(ranked, request.prefer_miles_program)

        return FlightSearchResponse(
            query=request,
            ranked_options=ranked,
            recommended_best_cash=best_cash,
            recommended_best_miles=best_miles,
            split_ticket_suggestions=split_suggestions,
            matched_promotions=match_promotions(request.origin, request.destination, request.date),
            strategic_recommendation=self._recommend_strategy(best_cash, best_miles, split_suggestions),
        )

    def _recommend_strategy(
        self,
        best_cash: RankedFlightOption | None,
        best_miles: RankedFlightOption | None,
        split_suggestions: list[RankedFlightOption],
    ) -> StrategyRecommendation:
        if split_suggestions:
            top_split = split_suggestions[0]
            return StrategyRecommendation(
                strategy="SPLIT_TICKET",
                reason=f"Combinação de trechos reduz custo para R$ {top_split.option.cash_price_brl}",
            )

        if best_miles and best_cash and best_miles.option.cash_price_brl <= best_cash.option.cash_price_brl * 1.1:
            return StrategyRecommendation(
                strategy="MILES",
                reason="Resgate com milhas apresenta bom valor relativo para a rota",
            )

        if best_cash:
            return StrategyRecommendation(
                strategy="CASH",
                reason="Compra em dinheiro é a opção mais eficiente no cenário atual",
            )

        return StrategyRecommendation(
            strategy="NO_OPTIONS",
            reason="Nenhuma opção disponível para os critérios da busca",
        )

    def _build_ranked_option(
        self,
        option: FlightOption,
        risk_level: RiskLevel = RiskLevel.low,
        reasons: list[str] | None = None,
    ) -> RankedFlightOption:
        return RankedFlightOption(
            option=option,
            total_duration_minutes=total_minutes(option),
            score=round(score_option(option), 2),
            value_per_mile_brl=value_per_mile(option),
            risk_level=risk_level,
            recommendation_reasons=reasons or [],
        )

    def _best_miles_option(self, ranked: list[RankedFlightOption], program) -> RankedFlightOption | None:
        candidates = [item for item in ranked if is_miles_good_deal(item.value_per_mile_brl, program)]
        if not candidates:
            return None
        winner = max(candidates, key=lambda item: item.value_per_mile_brl or 0)
        winner.recommendation_reasons.append("Melhor valor por milha para o programa selecionado")
        return winner

    async def _split_ticket_suggestions(
        self, origin: str, destination: str, travel_date: date, direct_best_price: float
    ) -> list[RankedFlightOption]:
        hubs = ["BSB", "CNF", "POA"]
        suggestions: list[RankedFlightOption] = []
        mock_provider = MockFlightProvider()

        for hub in hubs:
            if hub in (origin, destination):
                continue
            first_legs = await mock_provider.search(origin, hub, travel_date)
            second_legs = await mock_provider.search(hub, destination, travel_date)

            for first_leg in first_legs:
                for second_leg in second_legs:
                    connection_minutes = int(
                        (second_leg.departure_at - first_leg.arrival_at).total_seconds() // 60
                    )
                    if connection_minutes < self.min_connection_minutes:
                        continue

                    risk_level = self._risk_level(connection_minutes)
                    if risk_level == RiskLevel.high:
                        continue

                    combined_price = first_leg.cash_price_brl + second_leg.cash_price_brl
                    if combined_price >= direct_best_price:
                        continue

                    merged = FlightOption(
                        id=f"SPLIT-{origin}-{hub}-{destination}-{first_leg.id}-{second_leg.id}",
                        origin=origin,
                        destination=destination,
                        departure_at=first_leg.departure_at,
                        arrival_at=second_leg.arrival_at,
                        airline=f"{first_leg.airline}+{second_leg.airline}",
                        connections=1,
                        cash_price_brl=combined_price,
                        miles_price=(first_leg.miles_price or 0) + (second_leg.miles_price or 0),
                        taxes_brl=first_leg.taxes_brl + second_leg.taxes_brl,
                        source="split-engine",
                    )

                    reasons = [
                        f"Economia vs melhor direto: R$ {round(direct_best_price - combined_price, 2)}",
                        f"Conexão em {hub} de {connection_minutes} minutos",
                    ]
                    suggestions.append(self._build_ranked_option(merged, risk_level, reasons))

        return sorted(suggestions, key=lambda item: item.score)[:3]

    def _risk_level(self, connection_minutes: int) -> RiskLevel:
        if connection_minutes > self.max_connection_minutes:
            return RiskLevel.high
        if connection_minutes <= 120:
            return RiskLevel.medium
        return RiskLevel.low
