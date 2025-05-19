from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database_pg import get_db
from app.crud import subscribed

router = APIRouter(prefix="/subscribe", tags=["Subscriptions"])


class SymbolsRequest(BaseModel):
    symbols: List[str]
    price: Optional[float] = None  # optional price for all symbols


@router.post("/")
def add_symbols(request: SymbolsRequest, db: Session = Depends(get_db)):
    try:
        results = []
        for symbol in request.symbols:
            result = subscribed.add_subscribe_symbol(db, symbol, request.price)
            results.append(result)
        return {"added": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[str])
def all_symbols(db: Session = Depends(get_db)):
    return subscribed.get_subscribe_symbols(db)


@router.delete("/{symbol}")
def remove(symbol: str, db: Session = Depends(get_db)):
    subscribed.remove_subscribe_symbol(db, symbol)
    return {"message": f"{symbol.upper()} removed"}
