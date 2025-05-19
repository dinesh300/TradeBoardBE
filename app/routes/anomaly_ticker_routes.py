from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database_pg import get_db
from app.crud import anomaly_ticker

router = APIRouter(prefix="/anomaly-tickers", tags=["Anomaly Tickers"])


class TickerPayload(BaseModel):
    ticker: str
    type: str = "unknown"


@router.post("/")
def add(payload: TickerPayload, db: Session = Depends(get_db)):
    anomaly_ticker.add_anomaly_symbol(db, payload.ticker, payload.type)
    return {"message": f"{payload.ticker.upper()} added with type {payload.type}"}


@router.get("/", response_model=list[TickerPayload])
def all_tickers(db: Session = Depends(get_db)):
    return anomaly_ticker.get_anomaly_symbols(db)


@router.delete("/{ticker}")
def remove(ticker: str, db: Session = Depends(get_db)):
    anomaly_ticker.remove_anomaly_symbol(db, ticker)
    return {"message": f"{ticker.upper()} removed"}
