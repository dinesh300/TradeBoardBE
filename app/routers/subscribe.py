from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.crud.subscribe import (
    add_subscribe_symbol,
    remove_subscribe_symbol,
    get_subscribe_symbols,
)
from app.constants import DB_PATH
import sqlite3

router = APIRouter(prefix="/subscribe", tags=["Subscribe"])


class SymbolsRequest(BaseModel):
    symbols: List[str]


class SymbolsUnsubscribeRequest(BaseModel):
    symbols: List[str]


@router.post("/symbols")
def add_subscriptions(req: SymbolsRequest):
    try:
        for symbol in req.symbols:
            add_subscribe_symbol(symbol)
        return {"status": "symbols added", "symbols": [s.upper() for s in req.symbols]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding symbols: {str(e)}")


@router.get("/symbols")
def get_subscribed_symbols():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, last_trade_price FROM subscribed_symbols")
        rows = cursor.fetchall()

        result = [
            {
                "symbol": symbol.upper(),
                "lastTradePrice": price if price is not None else "N/A"
            }
            for symbol, price in rows
        ]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching symbols: {str(e)}")
    finally:
        conn.close()


@router.delete("/unsubscribe/symbols")
def unsubscribe_symbols(req: SymbolsUnsubscribeRequest):
    try:
        for symbol in req.symbols:
            remove_subscribe_symbol(symbol)
        return {
            "status": "success",
            "message": f"Symbols removed: {[s.upper() for s in req.symbols]}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing symbols: {str(e)}")
