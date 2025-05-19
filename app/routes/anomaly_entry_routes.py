from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
from app.database_pg import get_db
from app.crud import anomaly_entry
from app.schemas import AnomalyEntryCreate, AnomalyEntryResponse

router = APIRouter(prefix="/anomaly-entries", tags=["Anomaly Entries"])


@router.get("/", response_model=List[AnomalyEntryResponse])
def all_entries(db: Session = Depends(get_db)):
    entries = anomaly_entry.get_all_anomaly_entries(db)
    return entries


@router.delete("/{ticker}")
def delete_by_stock(ticker: str, db: Session = Depends(get_db)):
    anomaly_entry.delete_anomaly_entries_by_stock(db, ticker)
    return {"message": f"Entries for {ticker.upper()} deleted"}


@router.post("/", response_model=AnomalyEntryResponse)
def create_entry(entry: AnomalyEntryCreate, db: Session = Depends(get_db)):
    try:
        # Pass fields to your insert function (adjust if you renamed fields)
        db_entry = anomaly_entry.insert_anomaly_entry(
            db=db,
            ticker=entry.ticker,
            anomaly_type=entry.anomaly_type,
            market_open=entry.market_open,
            tpos=entry.tpos,
            action=entry.action,
            threshold_price=entry.threshold_price,
            price=entry.price,
            # If your insert function accepts timestamp, add it; otherwise ignore
        )
        return db_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticker}/action")
def update_action(ticker: str, action_text: str, db: Session = Depends(get_db)):
    anomaly_entry.update_anomaly_action(db, ticker, action_text)
    return {"message": f"Action updated for {ticker.upper()}"}


@router.put("/{ticker}/open-timeframe")
def update_open_tpos_action(
    ticker: str,
    open_price: float,
    timeframe: str,
    action: str,
    db: Session = Depends(get_db),
):
    anomaly_entry.update_open_and_timeframe(db, ticker, open_price, timeframe, action)
    return {"message": f"Open, timeframe and action updated for {ticker.upper()}"}


@router.put("/{ticker}/status")
def update_status(ticker: str, status: str, db: Session = Depends(get_db)):
    anomaly_entry.update_anomaly_status(db, ticker, status)
    return {"message": f"Status updated for {ticker.upper()}"}
