# sell_handler.py

from datetime import datetime
from config import insert_anomaly_entry, update_anomaly_open_and_timeframe, update_anomaly_action
from ws_manager import broadcast_threshold_update, broadcast_day_open_update
from constants import (
    STATUS_BREAKOUT,
    STATUS_NO_BREAKOUT,
    ACTION_NO_BREAKOUT,
    ACTION_BREAKOUT
)

# Trackers
LOW_TRACKER = {}
OPEN_PRICE_TRACKER_SELL = {}
LAST_TIMEFRAME_TRACKER_SELL = {}
PREVIOUS_TIMEFRAME_LOW = {}
PREVIOUS_TIMEFRAME_LABEL_SELL = {}
BREAKDOWN_RECORDED = {}
OPEN_UPDATED_FOR_A_SELL = {}


async def handle_sell_anomaly(ticker, anomaly_type, price, timeframe, time):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Handle open update only once during 'A' timeframe
    if timeframe == 'A' and ticker not in OPEN_UPDATED_FOR_A_SELL:
        update_anomaly_open_and_timeframe(ticker, price, timeframe, ACTION_NO_BREAKOUT)
        await broadcast_day_open_update(
            ticker.upper(),
            price,       # Market open price
            timeframe,   # Timeframe
            ACTION_NO_BREAKOUT
        )
        OPEN_UPDATED_FOR_A_SELL[ticker] = True
        OPEN_PRICE_TRACKER_SELL[ticker] = price
        print(f"Monitor for {ticker} (SELL) started at market open price {price} during timeframe {timeframe}")

    # Track lowest price in the current timeframe
    if ticker not in LOW_TRACKER:
        LOW_TRACKER[ticker] = price
    else:
        LOW_TRACKER[ticker] = min(LOW_TRACKER[ticker], price)

    # Timeframe has changed
    if ticker in LAST_TIMEFRAME_TRACKER_SELL and LAST_TIMEFRAME_TRACKER_SELL[ticker] != timeframe:
        previous_threshold = LOW_TRACKER.get(ticker, price)  # Store last timeframe's low
        PREVIOUS_TIMEFRAME_LOW[ticker] = previous_threshold
        PREVIOUS_TIMEFRAME_LABEL_SELL[ticker] = LAST_TIMEFRAME_TRACKER_SELL[ticker]

        # Insert anomaly entry for the completed timeframe
        insert_anomaly_entry(
            ticker=ticker,
            anomaly_type=anomaly_type,
            market_open=OPEN_PRICE_TRACKER_SELL.get(ticker, price),
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

        print(f"📥 Inserted SELL anomaly for {ticker} due to timeframe change to {timeframe}")

        # Reset for the new timeframe
        BREAKDOWN_RECORDED.pop(ticker, None)
        LOW_TRACKER[ticker] = price  # Start new low tracking for current timeframe

    else:
        # Use previous timeframe's low to detect breakdown
        threshold_price = PREVIOUS_TIMEFRAME_LOW.get(ticker)
        if threshold_price and price < threshold_price and not BREAKDOWN_RECORDED.get(ticker, False):
            update_anomaly_action(ticker.upper(), ACTION_BREAKOUT)

            await broadcast_threshold_update(
                ticker.upper(),
                threshold_price,
                timeframe,
                action=ACTION_BREAKOUT
            )

            print(f"🔻 Breakdown detected for {ticker} at price {price} < threshold {threshold_price}")
            BREAKDOWN_RECORDED[ticker] = True

    # Always update the last seen timeframe
    LAST_TIMEFRAME_TRACKER_SELL[ticker] = timeframe
