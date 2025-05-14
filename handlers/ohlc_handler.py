# handlers/ohlc_handler.py
from collections import defaultdict

# A defaultdict to store OHLC data for each ticker and timeframe
TICKER_OHLC = defaultdict(lambda: defaultdict(lambda: {"open": None, "high": float('-inf'), "low": float('inf')}))
SEEN_TICKER_TIMEFRAME = defaultdict(set)


def update_ohlc(ticker, timeframe, price):
    """
    Update the OHLC data for the given ticker and timeframe with the new price.
    - If it's the first time seeing the timeframe, the price will be set as the open price.
    - The high and low are updated accordingly.
    """
    tf_data = TICKER_OHLC[ticker][timeframe]

    # If the timeframe hasn't been seen yet, set the open price
    if timeframe not in SEEN_TICKER_TIMEFRAME[ticker]:
        tf_data["open"] = price
        SEEN_TICKER_TIMEFRAME[ticker].add(timeframe)

    # Update the high and low prices for the timeframe
    tf_data["high"] = max(tf_data["high"], price)
    tf_data["low"] = min(tf_data["low"], price)


def get_ohlc(ticker, timeframe):
    """
    Retrieve the OHLC data for a specific ticker and timeframe.
    """
    return TICKER_OHLC[ticker].get(timeframe, None)
