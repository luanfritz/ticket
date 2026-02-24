from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MilesProgram(str, Enum):
    latam_pass = "LATAM_PASS"
    smiles = "SMILES"
    tudo_azul = "TUDO_AZUL"


class RiskLevel(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"


class FlightOption(BaseModel):
    id: str
    origin: str
    destination: str
    departure_at: datetime
    arrival_at: datetime
    airline: str
    connections: int = Field(ge=0)
    cash_price_brl: float = Field(gt=0)
    miles_price: Optional[int] = Field(default=None, ge=0)
    taxes_brl: float = Field(default=0, ge=0)
    source: str


class RankedFlightOption(BaseModel):
    option: FlightOption
    total_duration_minutes: int
    score: float
    value_per_mile_brl: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.low
    recommendation_reasons: list[str] = Field(default_factory=list)


class FlightSearchRequest(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    date: date
    prefer_miles_program: Optional[MilesProgram] = None


class StrategyRecommendation(BaseModel):
    strategy: str
    reason: str


class FlightSearchResponse(BaseModel):
    query: FlightSearchRequest
    ranked_options: list[RankedFlightOption]
    recommended_best_cash: Optional[RankedFlightOption] = None
    recommended_best_miles: Optional[RankedFlightOption] = None
    split_ticket_suggestions: list[RankedFlightOption]
    matched_promotions: list[str]
    strategic_recommendation: StrategyRecommendation


class PromotionIn(BaseModel):
    route: str = Field(pattern=r"^[A-Z]{3}-[A-Z]{3}$")
    valid_from: date
    valid_to: date
    price_brl: float = Field(gt=0)
    source: str = Field(min_length=2)
    notes: str = Field(default="")


class PromotionOut(PromotionIn):
    pass


class PriceAlertIn(BaseModel):
    route: str = Field(pattern=r"^[A-Z]{3}-[A-Z]{3}$")
    target_price_brl: float = Field(gt=0)
    email: str = Field(min_length=5)


class PriceAlertOut(PriceAlertIn):
    id: int


class AlertCheckOut(BaseModel):
    route: str
    evaluated_price_brl: float
    triggered_alerts: list[PriceAlertOut]


class FareHistoryPoint(BaseModel):
    route: str
    observed_at: datetime
    price_brl: float


class FareForecast(BaseModel):
    route: str
    current_avg_brl: float
    projected_next_week_brl: float
    trend: str


class TransferBonusSimulationIn(BaseModel):
    base_miles: int = Field(gt=0)
    bonus_percent: int = Field(ge=0, le=200)


class TransferBonusSimulationOut(BaseModel):
    base_miles: int
    bonus_percent: int
    total_miles: int


class MultiCityRequest(BaseModel):
    cities: list[str] = Field(min_length=3, max_length=6)
    date: date


class MultiCityResponse(BaseModel):
    path: list[str]
    estimated_total_brl: float
    notes: str
