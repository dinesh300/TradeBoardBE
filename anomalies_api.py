from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List
from datetime import datetime
from config import (
    get_subscribe_symbols,
    add_subscribe_symbol,
    remove_subscribe_symbol,
    get_anomaly_symbols,
    add_anomaly_symbol,
    remove_anomaly_symbol,
    delete_anomaly_entries_by_stock,
    get_all_anomaly_entries
)
from db import DB_PATH  # centralize DB path

router = APIRouter()

# === Pydantic Models ===
class AnomalyEntry(BaseModel):
    type: str
    open: float
    low: float
    high: float
    close: float
    threshold: float
    ticker: str
    time: datetime = None

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

@router.post("/subscribe")
def add_subscriptions(req: SymbolsRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for symbol in req.symbols:
            cursor.execute(
                "INSERT OR IGNORE INTO subscribed_symbols (symbol) VALUES (?)",
                (symbol.upper(),)
            )
        conn.commit()
        return {"status": "symbols added", "symbols": req.symbols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/subscriptions")
def get_subscribed_symbols():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, last_trade_price FROM subscribed_symbols")
        rows = cursor.fetchall()

        # Return an array of objects for frontend compatibility
        result = [
            {
                "symbol": symbol,
                "lastTradePrice": price if price is not None else "N/A"
            }
            for symbol, price in rows
        ]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


class SymbolRequest(BaseModel):
    symbol: str  # Define the symbol as a string to delete

@router.delete("/unsubscribe/{symbol}")
def unsubscribe_symbol(symbol: str):
    try:
        remove_subscribe_symbol(symbol)  # Call the function to remove the symbol
        return {"status": "success", "message": f"Symbol {symbol.upper()} removed from subscriptions."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing symbol: {str(e)}")


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