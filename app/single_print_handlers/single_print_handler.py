from app.single_print_handlers.ohlc_handler import update_ohlc, get_ohlc
import asyncio
from app.ws_manager import broadcast_single_print

# Global SP memory (for demo only)
pending_single_prints = {}

def detect_single_print(ticker, current_tf, price):
    tf_order = [chr(i) for i in range(65, 78)]  # 'A' to 'M'
    if current_tf not in tf_order:
        return None

    idx = tf_order.index(current_tf)
    if idx < 2:
        return None  # Need at least tf[i-2]

    # Clean up old SPs
    cleanup_pending_sps(ticker, current_tf, price, tf_order)

    tf_sp = tf_order[idx - 1]           # tf[i-1] → used for breakout level
    tf_compare = tf_order[:idx - 1]     # tf[0] to tf[i-2] → used for open comparison

    # Update and fetch OHLC
    update_ohlc(ticker, current_tf, price)
    current_ohlc = get_ohlc(ticker, current_tf)
    sp_ohlc = get_ohlc(ticker, tf_sp)

    if not current_ohlc or not sp_ohlc or current_ohlc["open"] is None:
        return None

    # Gather tf[i-2] and earlier highs/lows (exclude tf[i-1])
    prev_ohlcs = [get_ohlc(ticker, tf) for tf in tf_compare]
    prev_highs = [ohlc["high"] for ohlc in prev_ohlcs if ohlc and ohlc["high"] is not None]
    prev_lows = [ohlc["low"] for ohlc in prev_ohlcs if ohlc and ohlc["low"] is not None]

    if not prev_highs or not prev_lows:
        return None

    sp_type = None
    breakout_level = None
    action = "No Breakout"

    # ✅ Buy SP Logic – open > all highs EXCEPT tf[i-1]
    if current_ohlc["open"] > max(prev_highs):
        sp_type = "buy"
        breakout_level = sp_ohlc["high"]
        if price > breakout_level:
            action = "Breakout"

    # ✅ Sell SP Logic – open < all lows EXCEPT tf[i-1]
    elif current_ohlc["open"] < min(prev_lows):
        sp_type = "sell"
        breakout_level = sp_ohlc["low"]
        if price < breakout_level:
            action = "Breakout"
    else:
        return None  # Not a valid SP

    # Prepare SP data
    sp_data = {
        "type": "single_print",
        "ticker": ticker,
        "spType": sp_type,
        "breakout": breakout_level,
        "ltp": price,
        "action": action,
        "status": "confirmed" if action == "Breakout" else "waiting",
        "timeframe": current_tf,
        "sp_timeframe": tf_sp
    }

    if action == "Breakout":
        asyncio.create_task(broadcast_single_print(sp_data))  # if you have this function
    else:
        pending_single_prints[ticker] = {
            "sp_data": sp_data,
            "start_idx": idx
        }

    return None


def cleanup_pending_sps(ticker, current_tf, price, tf_order):
    if ticker not in pending_single_prints:
        return

    current_idx = tf_order.index(current_tf)
    sp_entry = pending_single_prints[ticker]
    sp_data = sp_entry["sp_data"]
    sp_idx = sp_entry["start_idx"]
    sp_type = sp_data["spType"]
    breakout = sp_data["breakout"]

    # ✅ 1. Confirm breakout within tf[i+1] or tf[i+2]
    if current_idx in [sp_idx + 1, sp_idx + 2]:
        if (sp_type == "buy" and price > breakout) or (sp_type == "sell" and price < breakout):
            sp_data["ltp"] = price
            sp_data["action"] = "Breakout"
            sp_data["status"] = "confirmed"
            del pending_single_prints[ticker]
            asyncio.create_task(broadcast_single_print(sp_data))
            return

    # ❌ 2. Invalidate if open of tf[i+2] hits the SP zone
    if current_idx == sp_idx + 2:
        ohlc = get_ohlc(ticker, current_tf)
        if ohlc and ohlc["open"] is not None:
            if (sp_type == "buy" and ohlc["open"] <= breakout) or (sp_type == "sell" and ohlc["open"] >= breakout):
                print(f"❌ SP Invalidated for {ticker} at {current_tf}")
                del pending_single_prints[ticker]
