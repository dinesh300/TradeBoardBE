from sqlalchemy.orm import Session
from app.models import SubscribedSymbol


# ---------- Subscribe Symbol ----------
def get_subscribe_symbols(db: Session) -> list[str]:
    return [row.symbol for row in db.query(SubscribedSymbol).all()]


def add_subscribe_symbol(db: Session, symbol: str, price: float | None = None):
    obj = SubscribedSymbol(symbol=symbol.upper(), last_trade_price=price)
    db.merge(obj)           # merge → insert or update
    db.commit()
    return obj


def remove_subscribe_symbol(db: Session, symbol: str):
    db.query(SubscribedSymbol).filter(SubscribedSymbol.symbol == symbol.upper()).delete()
    db.commit()


def get_subscribed_symbols_with_price(db: Session) -> list[dict]:
    results = db.query(SubscribedSymbol).all()
    return [
        {
            "symbol": row.symbol,
            "lastTradePrice": row.last_trade_price
        }
        for row in results
    ]