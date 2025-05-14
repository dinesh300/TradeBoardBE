# buy_handler.py

from datetime import datetime
from config import insert_anomaly_entry, update_anomaly_open_and_timeframe,update_anomaly_action
from ws_manager import broadcast_threshold_update, broadcast_day_open_update
from constants import (
    STATUS_BREAKOUT,
    STATUS_NO_BREAKOUT,
    ACTION_NO_BREAKOUT,
    ACTION_BREAKOUT
)

# Trackers
HIGH_TRACKER = {}
OPEN_PRICE_TRACKER = {}
LAST_TIMEFRAME_TRACKER = {}
PREVIOUS_TIMEFRAME_HIGH = {}
PREVIOUS_TIMEFRAME_LABEL = {}
BREAKOUT_RECORDED = {}
OPEN_UPDATED_FOR_A = {}


async def handle_buy_anomaly(ticker, anomaly_type, price, timeframe, time):
    #print("Inside Handle_buy_anomaly method")
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Handle open update only once during 'A' timeframe
    if timeframe == 'A' and ticker not in OPEN_UPDATED_FOR_A:
        update_anomaly_open_and_timeframe(ticker, price, timeframe, ACTION_NO_BREAKOUT)
        await broadcast_day_open_update(
            ticker.upper(),
            price,       # Market open price
            timeframe,   # Timeframe
            ACTION_NO_BREAKOUT
        )
        OPEN_UPDATED_FOR_A[ticker] = True
        OPEN_PRICE_TRACKER[ticker] = price
        print(f"Monitor for {ticker} started at market open price {price} during timeframe {timeframe}")

    # Track highest price in the current timeframe
    if ticker not in HIGH_TRACKER:
        HIGH_TRACKER[ticker] = price
    else:
        HIGH_TRACKER[ticker] = max(HIGH_TRACKER[ticker], price)

    #print("Last timeframe tracker : ", LAST_TIMEFRAME_TRACKER)

    # Timeframe has changed
    if ticker in LAST_TIMEFRAME_TRACKER and LAST_TIMEFRAME_TRACKER[ticker] != timeframe:
        previous_threshold = HIGH_TRACKER.get(ticker, price)  # Store the last timeframe's high
        PREVIOUS_TIMEFRAME_HIGH[ticker] = previous_threshold
        PREVIOUS_TIMEFRAME_LABEL[ticker] = LAST_TIMEFRAME_TRACKER[ticker]

        # Insert anomaly entry for the completed timeframe
        insert_anomaly_entry(
            ticker=ticker,
            anomaly_type=anomaly_type,
            market_open=OPEN_PRICE_TRACKER.get(ticker, price),
            tpos=timeframe,
            action=ACTION_NO_BREAKOUT,
            threshold_price=previous_threshold,
            price=price,
            current_time=current_time
        )

        await broadcast_threshold_update(
            ticker.upper(),
            previous_threshold,
            timeframe,
            action=ACTION_NO_BREAKOUT
        )

        print(f"📥 Inserted anomaly for {ticker} due to timeframe change to {timeframe}")

        # Reset for the new timeframe
        BREAKOUT_RECORDED.pop(ticker, None)
        HIGH_TRACKER[ticker] = price  # start new high tracking for current timeframe

    else:
        # Use previous timeframe's high to detect breakout
        threshold_price = PREVIOUS_TIMEFRAME_HIGH.get(ticker)
        if threshold_price and price > threshold_price and not BREAKOUT_RECORDED.get(ticker, False):
            update_anomaly_action(ticker.upper(), ACTION_BREAKOUT)

            await broadcast_threshold_update(
                ticker.upper(),
                threshold_price,
                timeframe,
                action=ACTION_BREAKOUT
            )

            print(f"🚀 Breakout detected for {ticker} at price {price} > threshold {threshold_price}")
            BREAKOUT_RECORDED[ticker] = True

    # Always update the last seen timeframe
    LAST_TIMEFRAME_TRACKER[ticker] = timeframe
