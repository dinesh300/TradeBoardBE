# buy_handler.py
import sqlite3
from config import insert_anomaly_entry, update_anomaly_action, update_current_price, update_anomaly_status,update_anomaly_open_and_timeframe
from datetime import datetime
from config import DB_PATH

# Trackers
HIGH_TRACKER = {}
OPEN_PRICE_TRACKER = {}
LAST_TIMEFRAME_TRACKER = {}
PREVIOUS_TIMEFRAME_HIGH = {}
PREVIOUS_TIMEFRAME_LABEL = {}
BREAKOUT_RECORDED = {}
OPEN_UPDATED_FOR_L = {}


def handle_buy_anomaly1(ticker,anomaly_type, price, timeframe, time):
    print("Inside Handle_buy_anamoly method")
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    if timeframe == 'L' and not OPEN_UPDATED_FOR_L.get(ticker, False):
        update_anomaly_open_and_timeframe(ticker, price, timeframe)
        OPEN_UPDATED_FOR_L[ticker] = True

    # Track the open price at the start of timeframe
    if ticker not in OPEN_PRICE_TRACKER:
        OPEN_PRICE_TRACKER[ticker] = price
        #update_anomaly_open_and_timeframe(ticker, price, timeframe)
        print(f"Monitor for {ticker} started at market open price {price} during timeframe {timeframe}")

    # Track the high price during current timeframe
    if ticker not in HIGH_TRACKER:
        HIGH_TRACKER[ticker] = price
    else:
        HIGH_TRACKER[ticker] = max(HIGH_TRACKER[ticker], price)
    print("Last timeframe tracker : ", LAST_TIMEFRAME_TRACKER)
    # Handle timeframe change
    if ticker in LAST_TIMEFRAME_TRACKER and LAST_TIMEFRAME_TRACKER[ticker] != timeframe:
        print("Im inside insert_anomaly_entry loop")
        insert_anomaly_entry(
            ticker=ticker,
            anomaly_type= anomaly_type,
            market_open=OPEN_PRICE_TRACKER.get(ticker, price),
            tpos=timeframe,
            action="No Breakout",
            threshold_price=HIGH_TRACKER.get(ticker, price),
            price=price,
            current_time=current_time
        )
        print(f"📥 Inserted anomaly for {ticker} due to timeframe change to {timeframe}")

        PREVIOUS_TIMEFRAME_HIGH[ticker] = HIGH_TRACKER[ticker]
        PREVIOUS_TIMEFRAME_LABEL[ticker] = LAST_TIMEFRAME_TRACKER[ticker]
        BREAKOUT_RECORDED[ticker] = False

        OPEN_PRICE_TRACKER[ticker] = price
        HIGH_TRACKER[ticker] = price

    else:
        # Still in same timeframe, update current price for latest row
        #update_current_price(ticker, price)
        #print(f"✅ Updated current price for {ticker} to {price}")

        # Compare current price with threshold price to calculate percentage
        threshold_price = HIGH_TRACKER.get(ticker, price)
        percentage = calculate_percentage(price, threshold_price)

        # Log the calculated percentage (you can store this in your database if needed)
        print(f"📊 {ticker} - Current Price: {price}, Threshold Price: {threshold_price}, Percentage: {percentage}%")

        # Update the status in the database with the calculated percentage
        # Example of updating status based on calculated percentage
        status = f"{percentage}%"
        update_anomaly_status(ticker, status)

        # Check for breakout if not already recorded
        if ticker in PREVIOUS_TIMEFRAME_HIGH and not BREAKOUT_RECORDED.get(ticker, False):
            prev_high = PREVIOUS_TIMEFRAME_HIGH[ticker]
            prev_label = PREVIOUS_TIMEFRAME_LABEL[ticker]

            if price > prev_high:
                action_text = f"{timeframe} breakout {prev_label}"
                update_anomaly_action(ticker, action_text, f"{percentage}%")
                BREAKOUT_RECORDED[ticker] = True
                print(f"🔼 Breakout: {ticker} - {action_text}")
            else:
                update_anomaly_action(ticker, "No breakout", f"{percentage}%")
                BREAKOUT_RECORDED[ticker] = True
                print(f"🔽 No breakout for {ticker}")

    LAST_TIMEFRAME_TRACKER[ticker] = timeframe


def calculate_percentage(current_price, threshold_price):
    """ Calculate percentage based on the comparison between current price and threshold price. """
    if current_price == threshold_price:
        return 100  # 100% when the current price equals the threshold price
    elif current_price < threshold_price:
        # Calculate percentage decrease based on how much lower the current price is
        percentage = 100 - (threshold_price - current_price) / threshold_price * 100
        return round(max(85, percentage), 2)  # Ensure a minimum of 85% if current price is much lower
    else:
        # Calculate percentage increase based on how much higher the current price is
        percentage = (current_price / threshold_price) * 100
        return round(percentage, 2)  # Percentage increase above 100%
