from typing import Set
from fastapi import WebSocket
from constants import STATUS_NO_BREAKOUT, WS_MSG_TYPE_THRESHOLD_UPDATE

# Use a set for better performance and safety
connected_clients: Set[WebSocket] = set()


async def broadcast_trade_update(ticker: str, price: float):
    message = {
        "type": "trade_update",
        "symbol": ticker,
        "lastTradePrice": price
    }
    print(f"📤 Broadcasting Trade Update: {message} to {len(connected_clients)} clients")

    for client in connected_clients.copy():
        try:
            await client.send_json(message)
        except Exception as e:
            connected_clients.discard(client)
            print(f"❌ Removed client due to error: {e}")


async def broadcast_threshold_update(
        ticker: str,
        threshold_price: float,
        timeframe: str,
        action: str
):
    message = {
        "type": WS_MSG_TYPE_THRESHOLD_UPDATE,
        "symbol": ticker,
        "updatedThreshold": threshold_price,
        "timeframe": timeframe,
        "action": action,

    }
    print(f"📤 Broadcasting Threshold Update: {message} to {len(connected_clients)} clients")

    for client in connected_clients.copy():
        try:
            await client.send_json(message)
        except Exception as e:
            connected_clients.discard(client)
            print(f"❌ Removed client due to error: {e}")


async def broadcast_day_open_update(
    ticker: str,
    day_open_price: float,
    timeframe: str,
    action: str
):
    message = {
        "type": "day_open_update",
        "symbol": ticker,
        "dayOpenPrice": day_open_price,
        "timeframe": timeframe,
        "action": action
    }
    print(f"📤 Broadcasting Day Open and Timeframe Update: {message} to {len(connected_clients)} clients")

    for client in connected_clients.copy():
        try:
            await client.send_json(message)
        except Exception as e:
            connected_clients.discard(client)
            print(f"❌ Removed client due to error: {e}")

async def broadcast_new_anomaly(
        ticker: str,
        day_open_price: float,
        timeframe: str,
        action: str
):
    message = {
        "type": "add_new_anomaly",
        "symbol": ticker,
        "dayOpenPrice": day_open_price,
        "timeframe": timeframe,
        "action": action
    }
    print(f"📤 Broadcasting Day Open and Timeframe Update: {message} to {len(connected_clients)} clients")

    for client in connected_clients.copy():
        try:
            await client.send_json(message)
        except Exception as e:
            connected_clients.discard(client)
            print(f"❌ Removed client due to error: {e}")

