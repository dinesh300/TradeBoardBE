import asyncio
from datetime import datetime
from config import get_subscribe_symbols, load_anomaly_tickers
from anomaly_handlers.buy_handler import handle_buy_anomaly
from anomaly_handlers.sell_handler import handle_sell_anomaly
from pix_apidata import apidata_lib
from db import init_db
from ws_manager import broadcast_trade_update, broadcast_single_print
from handlers.ohlc_handler import update_ohlc
from handlers.single_print_handler import detect_single_print



api = apidata_lib.ApiData()
ANOMALY_TICKERS = {}

def get_timeframe_label(current_time):
    start_time = datetime(current_time.year, current_time.month, current_time.day, 9, 15)
    if start_time <= current_time <= start_time.replace(hour=15, minute=15):
        index = int((current_time - start_time).total_seconds() / 1800)
        return chr(65 + index) if index < 12 else None
    return None

def on_trade(msg):
    entries = msg if isinstance(msg, list) else [msg]
    now = datetime.now()
    timeframe = get_timeframe_label(now)
    if not timeframe:
        return

    for entry in entries:
        ticker = entry.get("ticker")
        price = entry.get("price")
        time = entry.get("time")

        # ✅ Send update to frontend
        asyncio.create_task(broadcast_trade_update(ticker, price,timeframe))
        # ✅ Update OHLC data
        update_ohlc(ticker, timeframe, price)

        # ✅ Detect single print
        #result = detect_single_print(ticker, timeframe, price)
        #if result:
            #print(f"🟢 Single Print ({result['type'].upper()}): {ticker} at {timeframe}")
            # sample_data = {
            #     "type": "single_print",
            #     "ticker": "AAPL",
            #     "spType": "buy",
            #     "breakout": 150.25,
            #     "ltp": 151.30,
            #     "action": "Breakout",
            #     "status": "confirmed",
            #     "timeframe": "A"
            # }
            # print("📤 Sending test single print to clients...")
            # asyncio.create_task(broadcast_single_print(sample_data))
            # # Optional: broadcast to clients
            # asyncio.create_task(broadcast_single_print(result))

        anomaly_type = ANOMALY_TICKERS.get(ticker)


        if anomaly_type and anomaly_type.strip().lower() == 'buy':
            print("Ticker : ", ticker, "Anamoly type : ", anomaly_type)
            asyncio.create_task(handle_buy_anomaly(ticker, anomaly_type, price, timeframe, time))
        elif anomaly_type and anomaly_type.strip().lower() == 'sell':
            print("Ticker : ", ticker, "Anamoly type : ", anomaly_type)
            asyncio.create_task(handle_sell_anomaly(ticker, anomaly_type, price, timeframe, time))

async def start_accelpix():
    init_db()

    global ANOMALY_TICKERS
    ANOMALY_TICKERS = load_anomaly_tickers()

    api.on_connection_started(lambda: print("✅ Accelpix Connected"))
    api.on_connection_stopped(lambda: print("❌ Accelpix Disconnected"))
    api.on_trade_update(on_trade)

    await api.initialize("WdcH05al5jj3VYKpb3DCpxU4AMk=", "apidata.accelpix.in")
    symbols = get_subscribe_symbols()
    await api.subscribeAll(symbols)
    print("📡 Subscribed to:", symbols)

def run_event_loop():
    loop = asyncio.get_event_loop()
    loop.create_task(start_accelpix())
    loop.run_forever()
