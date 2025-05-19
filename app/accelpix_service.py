import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_pg import SessionLocal

from app.anomaly_handlers.buy_handler import handle_buy_anomaly
from app.anomaly_handlers.sell_handler import handle_sell_anomaly
from app.utils.ohlc_handler import update_ohlc
from app.utils.single_print_handler import detect_single_print
#from pix_apidata import apidata_lib
from app.ws_manager import broadcast_trade_update
from app.crud.anomaly_ticker import load_anomaly_tickers
from app.crud.subscribed import get_subscribe_symbols
from app.constants import ANOMALY_TICKERS
from pix_apidata.apidata_lib import AccelpixApi

api = AccelpixApi()  # This should handle connection internally

def get_timeframe_label(current_time):
    start_time = datetime(current_time.year, current_time.month, current_time.day, 9, 15)
    if start_time <= current_time <= start_time.replace(hour=15, minute=15):
        index = int((current_time - start_time).total_seconds() / 1800)
        return chr(65 + index) if 0 <= index < 13 else None
    return None

def on_trade(msg):
    print("🔄 Trade message received:", msg)
    entries = msg if isinstance(msg, list) else [msg]
    now = datetime.now()
    timeframe = get_timeframe_label(now)
    if not timeframe:
        print("⏱️ Outside trading timeframe")
        return

    db: Session = SessionLocal()
    for entry in entries:
        ticker = entry.get("ticker")
        price = entry.get("price")
        time = entry.get("time")

        asyncio.create_task(broadcast_trade_update(ticker, price, timeframe))
        # update_ohlc(ticker, timeframe, price)
        # detect_single_print(ticker, timeframe, price)

        anomaly_type = ANOMALY_TICKERS.get(ticker)

        if anomaly_type and anomaly_type.strip().lower() == 'buy':
            print(f"📈 BUY -> Ticker: {ticker}, TPO: {timeframe}, Price: {price}")
            asyncio.create_task(handle_buy_anomaly(db, ticker, anomaly_type, price, timeframe, time))
        elif anomaly_type and anomaly_type.strip().lower() == 'sell':
            print(f"📉 SELL -> Ticker: {ticker}, TPO: {timeframe}, Price: {price}")
            asyncio.create_task(handle_sell_anomaly(db, ticker, anomaly_type, price, timeframe, time))

    db.close()




async def start_accelpix_loop():
    try:
        db = SessionLocal()
        subscribed = get_subscribed_symbols(db)
        symbols = [s.symbol for s in subscribed]

        print("Starting Accelpix connection...")
        await api.connect()  # Ensure this initializes and sets _ws correctly internally

        await api.subscribeAll(symbols)

        print("Subscribed to symbols:", symbols)

        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Exception in Accelpix loop: {e}")