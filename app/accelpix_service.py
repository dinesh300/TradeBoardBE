import asyncio
from datetime import datetime, time as dtime
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

def get_timeframe_label(trade_time: datetime):
    start = trade_time.replace(hour=9, minute=15, second=0, microsecond=0)
    end = trade_time.replace(hour=15, minute=15, second=0, microsecond=0)
    if start <= trade_time <= end:
        index = int((trade_time - start).total_seconds() / 1800)
        return chr(65 + index) if 0 <= index < 13 else None
    return None

def is_within_trading_time(unix_ts: int) -> tuple[bool, str | None, datetime | None]:
    dt = datetime.utcfromtimestamp(unix_ts)
    trade_time = dt.time()
    start_time = dtime(9, 15)
    end_time = dtime(15, 15)
    if start_time <= trade_time <= end_time:
        return True, get_timeframe_label(dt), dt
    return False, None, None

def on_trade(msg):
    print("🔄 Trade message received:", msg)
    entries = msg if isinstance(msg, list) else [msg]

    db: Session = SessionLocal()
    for entry in entries:
        ticker = entry.get("ticker")
        price = entry.get("price")
        unix_ts = entry.get("time")

        valid, timeframe, trade_dt = is_within_trading_time(unix_ts)
        if not valid:
            print("⏱️ Outside trading timeframe")
            continue

        asyncio.create_task(broadcast_trade_update(ticker, price, timeframe))
        # update_ohlc(ticker, timeframe, price)
        # detect_single_print(ticker, timeframe, price)

        anomaly_type = ANOMALY_TICKERS.get(ticker)

        if anomaly_type and anomaly_type.strip().lower() == 'buy':
            print(f"📈 BUY -> Ticker: {ticker}, TPO: {timeframe}, Price: {price}")
            asyncio.create_task(handle_buy_anomaly(db, ticker, anomaly_type, price, timeframe, unix_ts))
        elif anomaly_type and anomaly_type.strip().lower() == 'sell':
            print(f"📉 SELL -> Ticker: {ticker}, TPO: {timeframe}, Price: {price}")
            asyncio.create_task(handle_sell_anomaly(db, ticker, anomaly_type, price, timeframe, unix_ts))

    db.close()


async def start_accelpix_loop():
    print("🔁 Entered start_accelpix_loop")

    db = SessionLocal()
    try:
        tickers = load_anomaly_tickers(db)
        ANOMALY_TICKERS.update(tickers)
        print("📊 Loaded anomaly tickers:", tickers)
    except Exception as e:
        print("❌ Failed to load anomaly tickers:", e)
    finally:
        db.close()

    def on_connected():
        print("✅ Accelpix Connected")

    def on_disconnected():
        print("❌ Accelpix Disconnected")

    api.on_connection_started(on_connected)
    api.on_connection_stopped(on_disconnected)
    api.on_trade_update(on_trade)

    try:
        print("🔌 Initializing Accelpix...")
        await api.initialize("WdcH05al5jj3VYKpb3DCpxU4AMk=", "apidata.accelpix.in")
        print("🔐 Accelpix initialized")
    except Exception as e:
        print("❌ Failed to initialize Accelpix:", e)
        return

    db = SessionLocal()
    try:
        symbols = get_subscribe_symbols(db)
        await api.subscribeAll(symbols)
        print("📡 Subscribed to symbols:", symbols)
    except Exception as e:
        print("❌ Failed to subscribe to symbols:", e)
    finally:
        db.close()
