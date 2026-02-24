from datetime import datetime

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    AlertCheckOut,
    FareForecast,
    FareHistoryPoint,
    FlightSearchRequest,
    MilesProgram,
    MultiCityRequest,
    MultiCityResponse,
    PriceAlertIn,
    PriceAlertOut,
    PromotionIn,
    PromotionOut,
    TransferBonusSimulationIn,
    TransferBonusSimulationOut,
)
from app.services.engine import FlightEngine
from app.services.promotion_store import (
    StoredPromotion,
    add_fare_point,
    create_alert,
    fare_history,
    list_alerts,
    list_promotions,
    save_promotion,
    triggered_alerts,
)

app = FastAPI(title="Smart Fare Engine", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
engine = FlightEngine()


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/search")
async def search_flights(
    origin: str = Query(min_length=3, max_length=3),
    destination: str = Query(min_length=3, max_length=3),
    date: str = Query(description="YYYY-MM-DD"),
    prefer_miles_program: MilesProgram | None = None,
):
    request = FlightSearchRequest(
        origin=origin.upper(),
        destination=destination.upper(),
        date=date,
        prefer_miles_program=prefer_miles_program,
    )
    response = await engine.search(request)
    if response.recommended_best_cash:
        route = f"{request.origin}-{request.destination}"
        add_fare_point(route, datetime.utcnow(), response.recommended_best_cash.option.cash_price_brl)
    return response


@app.post("/api/v1/promotions", response_model=PromotionOut)
async def create_promotion(payload: PromotionIn):
    normalized_route = payload.route.upper()
    promotion = StoredPromotion(
        route=normalized_route,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        price_brl=payload.price_brl,
        source=payload.source,
        notes=payload.notes,
    )
    save_promotion(promotion)
    return PromotionOut(**payload.model_dump(), route=normalized_route)


@app.get("/api/v1/promotions", response_model=list[PromotionOut])
async def get_promotions(route: str | None = None):
    normalized_route = route.upper() if route else None
    rows = list_promotions(normalized_route)
    return [PromotionOut(**item.__dict__) for item in rows]


@app.post("/api/v1/alerts", response_model=PriceAlertOut)
async def create_price_alert(payload: PriceAlertIn):
    row = create_alert(payload.route.upper(), payload.target_price_brl, payload.email)
    return PriceAlertOut(id=row.id, route=row.route, target_price_brl=row.target_price_brl, email=row.email)


@app.get("/api/v1/alerts", response_model=list[PriceAlertOut])
async def get_price_alerts(route: str | None = None):
    normalized_route = route.upper() if route else None
    rows = list_alerts(normalized_route)
    return [
        PriceAlertOut(id=item.id, route=item.route, target_price_brl=item.target_price_brl, email=item.email)
        for item in rows
    ]


@app.get("/api/v1/alerts/check", response_model=AlertCheckOut)
async def check_alerts(route: str, price_brl: float):
    normalized_route = route.upper()
    matches = triggered_alerts(normalized_route, price_brl)
    return AlertCheckOut(
        route=normalized_route,
        evaluated_price_brl=price_brl,
        triggered_alerts=[
            PriceAlertOut(id=item.id, route=item.route, target_price_brl=item.target_price_brl, email=item.email)
            for item in matches
        ],
    )


@app.get("/api/v1/history/{route}", response_model=list[FareHistoryPoint])
async def get_fare_history(route: str):
    rows = fare_history(route.upper())
    return [FareHistoryPoint(route=item.route, observed_at=item.observed_at, price_brl=item.price_brl) for item in rows]


@app.get("/api/v1/forecast/{route}", response_model=FareForecast)
async def fare_forecast(route: str):
    rows = fare_history(route.upper())
    if not rows:
        return FareForecast(route=route.upper(), current_avg_brl=0, projected_next_week_brl=0, trend="NO_DATA")
    prices = [item.price_brl for item in rows]
    current_avg = round(sum(prices) / len(prices), 2)
    projected = round(current_avg * 0.98, 2)
    trend = "FALLING" if projected < current_avg else "STABLE"
    return FareForecast(route=route.upper(), current_avg_brl=current_avg, projected_next_week_brl=projected, trend=trend)


@app.post("/api/v1/simulate/transfer-bonus", response_model=TransferBonusSimulationOut)
async def simulate_transfer_bonus(payload: TransferBonusSimulationIn):
    total = int(payload.base_miles * (1 + payload.bonus_percent / 100))
    return TransferBonusSimulationOut(base_miles=payload.base_miles, bonus_percent=payload.bonus_percent, total_miles=total)


@app.post("/api/v1/multicity/recommendation", response_model=MultiCityResponse)
async def multicity_recommendation(payload: MultiCityRequest):
    path = [city.upper() for city in payload.cities]
    legs = len(path) - 1
    estimated_total_brl = float(legs * 650)
    return MultiCityResponse(
        path=path,
        estimated_total_brl=estimated_total_brl,
        notes="Estimativa inicial baseada em tarifa média por trecho",
    )
