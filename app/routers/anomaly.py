from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.crud.anomaly import add_anomaly_symbol
from app.crud.anomaly import (get_anomaly_symbols,remove_anomaly_symbol, get_all_anomaly_entries, delete_anomaly_entries_by_stock)
from pydantic import BaseModel

router = APIRouter(prefix="/anomaly", tags=["Anomaly"])

class TickerInput(BaseModel):
    ticker: str
    type: str = "generic"

class SymbolsRequest(BaseModel):
    symbols: List[str]

# === API Endpoints ===

@router.post("/anomaly-tickers")
def add_anomaly_ticker(ticker_input: TickerInput):
    try:
        add_anomaly_symbol(ticker_input.ticker, ticker_input.type)
        return {"message": f"{ticker_input.ticker.upper()} added to anomaly ticker list"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomaly-tickers", response_model=List[TickerInput])
def get_anomaly_tickers():
    try:
        return get_anomaly_symbols()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/anomaly-tickers")
def remove_anomaly_ticker(ticker_input: TickerInput):
    try:
        remove_anomaly_symbol(ticker_input.ticker)
        return {"message": f"{ticker_input.ticker.upper()} removed from anomaly ticker list"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Assuming you already have the `get_all_anomaly_entries` function
@router.get("/anomaly-entries", response_model=List[dict])
def fetch_all_anomaly_entries():
    try:
        # Fetch all anomaly entries
        entries = get_all_anomaly_entries()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching anomaly entries: {str(e)}")

@router.delete("/anomaly-entries/{ticker}")
def delete_anomaly_entries(ticker: str):
    try:
        delete_anomaly_entries_by_stock(ticker)
        return {"message": f"Anomaly entries for '{ticker}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

