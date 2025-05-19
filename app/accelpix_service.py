import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_pg import SessionLocal

from app.anomaly_handlers.buy_handler import handle_buy_anomaly
from app.anomaly_handlers.sell_handler import handle_sell_anomaly
from app.utils.ohlc_handler import update_ohlc
from app.utils.single_print_handler import detect_single_print
from pix_apidata import apidata_lib
from app.ws_manager import broadcast_trade_update, broadcast_random_counter
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
    print("🔁 Entered start_accelpix_loop")
    print("🚀 Starting broadcast_random_counter task")
    asyncio.create_task(broadcast_random_counter())
    # Load anomaly tickers
    db = SessionLocal()
    try:
        tickers = load_anomaly_tickers(db)
        ANOMALY_TICKERS.update(tickers)
        print("📊 Loaded anomaly tickers:", tickers)
    except Exception as e:
        print("❌ Failed to load anomaly tickers:", e)
    finally:
        db.close()

    # Setup event handlers
    def on_connected():
        print("✅ Accelpix Connected")

    def on_disconnected():
        print("❌ Accelpix Disconnected")

    api.on_connection_started(on_connected)
    api.on_connection_stopped(on_disconnected)
    api.on_trade_update(on_trade)

    # Initialize Accelpix connection
    try:
        print("🔌 Initializing Accelpix...")
        await api.initialize("WdcH05al5jj3VYKpb3DCpxU4AMk=", "apidata.accelpix.in")
        print("🔐 Accelpix initialized")
    except Exception as e:
        print("❌ Failed to initialize Accelpix:", e)
        return

    # Subscribe to symbols
    db = SessionLocal()
    try:
        symbols = get_subscribe_symbols(db)
        await api.subscribeAll(symbols)
        print("📡 Subscribed to symbols:", symbols)
    except Exception as e:
        print("❌ Failed to subscribe to symbols:", e)
    finally:
        db.close()
