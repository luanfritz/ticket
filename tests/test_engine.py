import asyncio
from datetime import date

from app.models import FlightSearchRequest, MilesProgram
from app.services.engine import FlightEngine


def test_engine_returns_ranked_options():
    engine = FlightEngine()
    response = asyncio.run(
        engine.search(
            FlightSearchRequest(
                origin="GRU",
                destination="REC",
                date=date(2026, 3, 10),
                prefer_miles_program=MilesProgram.latam_pass,
            )
        )
    )

    assert len(response.ranked_options) > 0
    assert response.recommended_best_cash is not None
    assert response.matched_promotions


def test_engine_split_suggestions_are_cheaper_than_best_direct():
    engine = FlightEngine()
    response = asyncio.run(
        engine.search(
            FlightSearchRequest(
                origin="GRU",
                destination="REC",
                date=date(2026, 3, 10),
            )
        )
    )

    best_direct = response.recommended_best_cash.option.cash_price_brl
    assert all(item.option.cash_price_brl < best_direct for item in response.split_ticket_suggestions)


def test_engine_marks_best_miles_recommendation_when_program_is_provided():
    engine = FlightEngine()
    response = asyncio.run(
        engine.search(
            FlightSearchRequest(
                origin="GRU",
                destination="REC",
                date=date(2026, 3, 10),
                prefer_miles_program=MilesProgram.smiles,
            )
        )
    )

    assert response.recommended_best_miles is not None
    assert response.recommended_best_miles.recommendation_reasons


def test_engine_returns_strategy_recommendation():
    engine = FlightEngine()
    response = asyncio.run(
        engine.search(
            FlightSearchRequest(
                origin="GRU",
                destination="REC",
                date=date(2026, 3, 10),
            )
        )
    )

    assert response.strategic_recommendation.strategy in {"CASH", "MILES", "SPLIT_TICKET", "NO_OPTIONS"}
