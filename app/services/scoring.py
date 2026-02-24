from app.models import FlightOption


class ScoringConfig:
    time_weight: float = 0.45
    connection_penalty: float = 120.0


def total_minutes(option: FlightOption) -> int:
    return int((option.arrival_at - option.departure_at).total_seconds() // 60)


def score_option(option: FlightOption, config: ScoringConfig | None = None) -> float:
    active_config = config or ScoringConfig()
    return (
        option.cash_price_brl
        + (total_minutes(option) * active_config.time_weight)
        + (option.connections * active_config.connection_penalty)
    )


def value_per_mile(option: FlightOption) -> float | None:
    if not option.miles_price or option.miles_price <= 0:
        return None
    return round((option.cash_price_brl - option.taxes_brl) / option.miles_price, 4)
