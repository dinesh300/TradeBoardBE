# handlers/single_print_handler.py

from handlers.ohlc_handler import update_ohlc, get_ohlc  # Get OHLC data

def detect_single_print(ticker, current_tf, price):
    """
    Detect single print for Buy/Sell based on open vs. previous TF's high/low.
    If open > previous high => Buy SP
    If open < previous low => Sell SP
    Also checks breakout.
    """
    tf_order = [chr(i) for i in range(65, 88)]  # 'A' to 'X'

    if current_tf not in tf_order:
        return None

    idx = tf_order.index(current_tf)
    if idx < 1:
        return None  # Need at least 1 previous TF

    tf_prev = tf_order[idx - 1]

    # Update OHLC with new price
    update_ohlc(ticker, current_tf, price)
    current_ohlc = get_ohlc(ticker, current_tf)
    prev_ohlc = get_ohlc(ticker, tf_prev)

    if not current_ohlc or not prev_ohlc or current_ohlc["open"] is None:
        return None

    breakout = None
    sp_type = None
    action = "No Breakout"

    if current_ohlc["open"] > prev_ohlc["high"]:
        sp_type = "buy"
        breakout = prev_ohlc["high"]
        if price > breakout:
            action = "Breakout"
    elif current_ohlc["open"] < prev_ohlc["low"]:
        sp_type = "sell"
        breakout = prev_ohlc["low"]
        if price < breakout:
            action = "Breakout"
    else:
        return None  # No SP

    return {
        "type": "single_print",
        "ticker     ": ticker,
        "spType": sp_type,
        "breakout": breakout,
        "ltp": price,
        "action": action,
        "status": "confirmed",
        "timeframe": current_tf
    }

