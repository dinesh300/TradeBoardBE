import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_pg import SessionLocal  # Adjust import to your actual DB session factory

from app.anomaly_handlers.buy_handler import handle_buy_anomaly
from app.anomaly_handlers.sell_handler import handle_sell_anomaly
from app.utils.ohlc_handler import update_ohlc
from app.utils.single_print_handler import detect_single_print
from pix_apidata import apidata_lib
from app.ws_manager import broadcast_trade_update
from app.crud.anomaly_ticker import load_anomaly_tickers
from app.crud.subscribed import get_subscribe_symbols
from app.constants import ANOMALY_TICKERS

api = apidata_lib.ApiData()


def get_timeframe_label(current_time):
    start_time = datetime(current_time.year, current_time.month, current_time.day, 9, 15)
    if start_time <= current_time <= start_time.replace(hour=15, minute=15):
        index = int((current_time - start_time).total_seconds() / 1800)
        return chr(65 + index) if 0 <= index < 13 else None
    return None


def on_trade(msg):
    print("🔄 Trade message received:", msg)  # For debugging
    entries = msg if isinstance(msg, list) else [msg]
    now = datetime.now()
    timeframe = get_timeframe_label(now)
    if not timeframe:
        return

    # Create a new DB session per call (remember to close it after use)
    db: Session = SessionLocal()

    for entry in entries:
        ticker = entry.get("ticker")
        price = entry.get("price")
        time = entry.get("time")

        # Send update to frontend
        asyncio.create_task(broadcast_trade_update(ticker, price, timeframe))
        # Update OHLC data
        #update_ohlc(ticker, timeframe, price)
        # Detect single print (Buy side logic only for now)
        #detect_single_print(ticker, timeframe, price)

        anomaly_type = ANOMALY_TICKERS.get(ticker)

        if anomaly_type and anomaly_type.strip().lower() == 'buy':
            print(f"Ticker: {ticker}, Anomaly type: {anomaly_type}, TPO: {timeframe}, Price: {price}")
            asyncio.create_task(handle_buy_anomaly(db, ticker, anomaly_type, price, timeframe, time))
        elif anomaly_type and anomaly_type.strip().lower() == 'sell':
            print(f"Ticker: {ticker}, Anomaly type: {anomaly_type}, TPO: {timeframe}, Price: {price}")
            asyncio.create_task(handle_sell_anomaly(db, ticker, anomaly_type, price, timeframe, time))

    # Close DB session to avoid leaks
    db.close()


async def start_accelpix_loop():
    db = SessionLocal()  # Create session
    try:
        ANOMALY_TICKERS.update(load_anomaly_tickers(db))
    finally:
        db.close()  # Always close session after use

    api.on_connection_started(lambda: print("✅ Accelpix Connected"))
    api.on_connection_stopped(lambda: print("❌ Accelpix Disconnected"))
    api.on_trade_update(on_trade)

    await api.initialize("WdcH05al5jj3VYKpb3DCpxU4AMk=", "apidata.accelpix.in")
    symbols = get_subscribe_symbols(db)
    await api.subscribeAll(symbols)
    print("📡 Subscribed to:", symbols)
