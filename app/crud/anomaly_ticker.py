from sqlalchemy.orm import Session
from datetime import datetime
from app.models import AnomalyTicker, AnomalyEntry
from app.constants import (
    STATUS_NO_BREAKOUT, ACTION_NO_BREAKOUT,
    DEFAULT_PRICE, DEFAULT_TIMEFRAME
)


# ---------- Anomaly Ticker ----------
def get_anomaly_symbols(db: Session) -> list[dict]:
    rows = db.query(AnomalyTicker).all()
    return [{"ticker": r.ticker, "type": r.type} for r in rows]


def add_anomaly_symbol(db: Session, symbol: str, type_: str = "unknown"):
    # upsert into anomaly_tickers
    db.merge(AnomalyTicker(ticker=symbol.upper(), type=type_.lower()))

    # always insert a matching AnomalyEntry “stub”
    entry = AnomalyEntry(
        stock=symbol.upper(),
        anomaly_type=type_.lower(),
        market_open=DEFAULT_PRICE,
        tpos=DEFAULT_TIMEFRAME,
        action=ACTION_NO_BREAKOUT,
        status=STATUS_NO_BREAKOUT,
        current_price=DEFAULT_PRICE,
        threshold_price=DEFAULT_PRICE,
        time=datetime.utcnow()
    )
    db.add(entry)
    db.commit()


def remove_anomaly_symbol(db: Session, symbol: str):
    db.query(AnomalyTicker).filter(AnomalyTicker.ticker == symbol.upper()).delete()
    db.query(AnomalyEntry).filter(AnomalyEntry.stock == symbol.upper()).delete()
    db.commit()


def load_anomaly_tickers(db: Session) -> dict[str, str]:
    """Return {TICKER: type} to sync in-memory caches."""
    return {row.ticker.upper(): row.type.lower() for row in db.query(AnomalyTicker).all()}
