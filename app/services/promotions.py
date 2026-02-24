from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Promotion:
    route: str
    valid_from: date
    valid_to: date
    message: str


PROMOTIONS = [
    Promotion(
        route="GRU-REC",
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
        message="Promo relâmpago GRU→REC por tempo limitado",
    ),
    Promotion(
        route="CGH-SSA",
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 6, 30),
        message="Tarifa promocional para Salvador",
    ),
]


def match_promotions(origin: str, destination: str, travel_date: date) -> list[str]:
    route = f"{origin}-{destination}"
    return [
        promo.message
        for promo in PROMOTIONS
        if promo.route == route and promo.valid_from <= travel_date <= promo.valid_to
    ]
