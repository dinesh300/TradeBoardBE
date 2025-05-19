from sqlalchemy import Column, String, Float, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TickerData(Base):
    __tablename__ = 'ticker_data'
    ticker = Column(String, primary_key=True, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    avg = Column(Float)
    oi = Column(Integer)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)

class SubscribedSymbol(Base):
    __tablename__ = 'subscribed_symbols'
    symbol = Column(String, primary_key=True, index=True)
    last_trade_price = Column(Float)

# ───────────────────────────────────────── anomaly_tickers
class AnomalyTicker(Base):
    __tablename__ = "anomaly_tickers"
    ticker = Column(String, primary_key=True, index=True)
    type   = Column(String, default="unknown")

class AnomalyEntry(Base):
    __tablename__ = 'anomalies_entry'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stock = Column(String)
    anomaly_type = Column(String)
    market_open = Column(Float)
    tpos = Column(String)
    action = Column(String)
    threshold_price = Column(Float)
    status = Column(String)
    current_price = Column(Float)
    time = Column(TIMESTAMP, default=datetime.utcnow)
