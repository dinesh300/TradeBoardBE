from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.anomaly_entry import (
    insert_anomaly_entry,
    update_open_and_timeframe,
    update_anomaly_action
)
from app.ws_manager import broadcast_threshold_update, broadcast_day_open_update
from app.constants import ACTION_NO_BREAKOUT, ACTION_BREAKOUT

# Trackers for anomaly logic
HIGH_TRACKER = {}
OPEN_PRICE_TRACKER = {}
LAST_TIMEFRAME_TRACKER = {}
PREVIOUS_TIMEFRAME_HIGH = {}
PREVIOUS_TIMEFRAME_LABEL = {}
BREAKOUT_RECORDED = {}
OPEN_UPDATED_FOR_A = {}

async def handle_buy_anomaly(
    db: Session,
    ticker: str,
    anomaly_type: str,
    price: float,
    timeframe: str,
    time: str
):
    """
    Main handler for detecting and inserting buy anomalies based on price action across timeframes.
    """
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Step 1: Capture open during timeframe 'A'
    if timeframe == 'A' and ticker not in OPEN_UPDATED_FOR_A:
        update_open_and_timeframe(db, ticker, price, timeframe, ACTION_NO_BREAKOUT)
        await broadcast_day_open_update(ticker.upper(), price, timeframe, ACTION_NO_BREAKOUT)
        OPEN_UPDATED_FOR_A[ticker] = True
        OPEN_PRICE_TRACKER[ticker] = price
        print(f"🔔 Monitoring started for {ticker} | Open: {price} | Timeframe: {timeframe}")

    # Step 2: Track high for current timeframe
    HIGH_TRACKER[ticker] = max(HIGH_TRACKER.get(ticker, price), price)

    # Step 3: Detect timeframe transition
    if ticker in LAST_TIMEFRAME_TRACKER and LAST_TIMEFRAME_TRACKER[ticker] != timeframe:
        prev_timeframe = LAST_TIMEFRAME_TRACKER[ticker]
        threshold_price = HIGH_TRACKER.get(ticker, price)
        PREVIOUS_TIMEFRAME_HIGH[ticker] = threshold_price
        PREVIOUS_TIMEFRAME_LABEL[ticker] = prev_timeframe

        # Insert anomaly for completed timeframe
        insert_anomaly_entry(
            db=db,
            ticker=ticker,
            anomaly_type=anomaly_type,
            market_open=OPEN_PRICE_TRACKER.get(ticker, price),
            tpos=timeframe,
            action=ACTION_NO_BREAKOUT,
            threshold_price=threshold_price,
            price=price
        )

        await broadcast_threshold_update(ticker.upper(), threshold_price, timeframe, ACTION_NO_BREAKOUT)
        print(f"📥 Anomaly logged for {ticker} | Threshold: {threshold_price} | New TF: {timeframe}")

        BREAKOUT_RECORDED.pop(ticker, None)
        HIGH_TRACKER[ticker] = price  # reset high for new timeframe

    else:
        # Step 4: Detect breakout
        threshold_price = PREVIOUS_TIMEFRAME_HIGH.get(ticker)
        if threshold_price and price > threshold_price and not BREAKOUT_RECORDED.get(ticker, False):
            update_anomaly_action(db, ticker.upper(), ACTION_BREAKOUT)
            await broadcast_threshold_update(ticker.upper(), threshold_price, timeframe, ACTION_BREAKOUT)
            print(f"🚀 Breakout detected for {ticker} | Price: {price} > Threshold: {threshold_price}")
            BREAKOUT_RECORDED[ticker] = True

    # Step 5: Update last seen timeframe
    LAST_TIMEFRAME_TRACKER[ticker] = timeframe
