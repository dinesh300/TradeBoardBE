from sqlalchemy.orm import Session
from datetime import datetime
from app.models import AnomalyEntry


# ---------- insert / update helpers ----------
def insert_anomaly_entry(
    db: Session,
    ticker: str,
    anomaly_type: str,
    market_open: float,
    tpos: str,
    action: str,
    threshold_price: float,
    price: float,
):
    entry = AnomalyEntry(
        stock=ticker.upper(),
        anomaly_type=anomaly_type.lower(),
        market_open=market_open,
        tpos=tpos,
        action=action,
        status="no_status",     # override if you have a constant
        current_price=price,
        threshold_price=threshold_price,
        time=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_anomaly_action(db: Session, ticker: str, action_text: str):
    latest = (
        db.query(AnomalyEntry)
        .filter(AnomalyEntry.stock == ticker.upper())
        .order_by(AnomalyEntry.time.desc())
        .first()
    )
    if latest:
        latest.action = action_text
        db.commit()


def update_open_and_timeframe(db: Session, ticker: str, open_price: float, timeframe: str, action: str):
    latest = (
        db.query(AnomalyEntry)
        .filter(AnomalyEntry.stock == ticker.upper())
        .order_by(AnomalyEntry.time.desc())
        .first()
    )
    if latest:
        latest.market_open = open_price
        latest.tpos = timeframe
        latest.action = action
        db.commit()


def update_anomaly_status(db: Session, ticker: str, status: str):
    latest = (
        db.query(AnomalyEntry)
        .filter(AnomalyEntry.stock == ticker.upper())
        .order_by(AnomalyEntry.time.desc())
        .first()
    )
    if latest:
        latest.status = status
        db.commit()


# ---------- bulk helpers ----------
def get_all_anomaly_entries(db: Session):
    return db.query(AnomalyEntry).all()


def delete_anomaly_entries_by_stock(db: Session, ticker: str):
    db.query(AnomalyEntry).filter(AnomalyEntry.stock == ticker.upper()).delete()
    db.commit()
