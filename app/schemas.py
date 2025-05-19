from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnomalyEntryResponse(BaseModel):
    id: int
    stock: str
    anomaly_type: str
    market_open: float
    tpos: str
    action: str
    status: str
    current_price: float
    threshold_price: float
    time: datetime

    class Config:
        orm_mode = True

class AnomalyEntryCreate(BaseModel):
    ticker: str
    anomaly_type: str
    market_open: float
    tpos: str
    action: str
    threshold_price: float
    price: float
    timestamp: Optional[datetime] = None  # Optional, if you want to allow passing timestamp

    class Config:
        orm_mode = True
