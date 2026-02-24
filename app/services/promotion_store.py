import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data.db"


@dataclass(frozen=True)
class StoredPromotion:
    route: str
    valid_from: date
    valid_to: date
    price_brl: float
    source: str
    notes: str


@dataclass(frozen=True)
class StoredAlert:
    id: int
    route: str
    target_price_brl: float
    email: str


@dataclass(frozen=True)
class StoredFarePoint:
    route: str
    observed_at: datetime
    price_brl: float


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_store() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route TEXT NOT NULL,
                valid_from TEXT NOT NULL,
                valid_to TEXT NOT NULL,
                price_brl REAL NOT NULL,
                source TEXT NOT NULL,
                notes TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route TEXT NOT NULL,
                target_price_brl REAL NOT NULL,
                email TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fare_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                price_brl REAL NOT NULL
            )
            """
        )


def save_promotion(promo: StoredPromotion) -> None:
    initialize_store()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO promotions (route, valid_from, valid_to, price_brl, source, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                promo.route,
                promo.valid_from.isoformat(),
                promo.valid_to.isoformat(),
                promo.price_brl,
                promo.source,
                promo.notes,
            ),
        )


def list_promotions(route: str | None = None) -> list[StoredPromotion]:
    initialize_store()
    query = "SELECT route, valid_from, valid_to, price_brl, source, notes FROM promotions"
    params: tuple[str, ...] = ()
    if route:
        query += " WHERE route = ?"
        params = (route,)
    query += " ORDER BY valid_from ASC"

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        StoredPromotion(
            route=row["route"],
            valid_from=date.fromisoformat(row["valid_from"]),
            valid_to=date.fromisoformat(row["valid_to"]),
            price_brl=float(row["price_brl"]),
            source=row["source"],
            notes=row["notes"],
        )
        for row in rows
    ]


def create_alert(route: str, target_price_brl: float, email: str) -> StoredAlert:
    initialize_store()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO alerts (route, target_price_brl, email) VALUES (?, ?, ?)",
            (route, target_price_brl, email),
        )
        alert_id = cur.lastrowid
    return StoredAlert(id=int(alert_id), route=route, target_price_brl=target_price_brl, email=email)


def list_alerts(route: str | None = None) -> list[StoredAlert]:
    initialize_store()
    query = "SELECT id, route, target_price_brl, email FROM alerts"
    params: tuple[str, ...] = ()
    if route:
        query += " WHERE route = ?"
        params = (route,)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        StoredAlert(
            id=int(row["id"]),
            route=row["route"],
            target_price_brl=float(row["target_price_brl"]),
            email=row["email"],
        )
        for row in rows
    ]


def add_fare_point(route: str, observed_at: datetime, price_brl: float) -> None:
    initialize_store()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO fare_history (route, observed_at, price_brl) VALUES (?, ?, ?)",
            (route, observed_at.isoformat(), price_brl),
        )


def fare_history(route: str) -> list[StoredFarePoint]:
    initialize_store()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT route, observed_at, price_brl FROM fare_history WHERE route = ? ORDER BY observed_at ASC",
            (route,),
        ).fetchall()
    return [
        StoredFarePoint(
            route=row["route"],
            observed_at=datetime.fromisoformat(row["observed_at"]),
            price_brl=float(row["price_brl"]),
        )
        for row in rows
    ]


def triggered_alerts(route: str, current_price_brl: float) -> list[StoredAlert]:
    candidates = list_alerts(route)
    return [item for item in candidates if current_price_brl <= item.target_price_brl]
