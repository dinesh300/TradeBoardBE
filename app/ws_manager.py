from typing import Set
from fastapi import WebSocket
from app.constants import STATUS_NO_BREAKOUT, WS_MSG_TYPE_THRESHOLD_UPDATE
import asyncio
import random
# Use a set for better performance and safety
connected_clients: Set[WebSocket] = set()


async def broadcast_trade_update(ticker: str, price: float, timeframe:str):
    message = {
        "type": "trade_update",
        "symbol": ticker,
        "lastTradePrice": price,
        "timeframe": timeframe,
    }
    #print(f"📤 Broadcasting Trade Update: {message} to {len(connected_clients)} clients")

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



async def broadcast_single_print(result: dict):
    message = {
        "type": "single_print",
        "symbol": result["ticker"],
        "spType": result["spType"],
        "breakout": result["breakout"],
        "ltp": result["ltp"],
        "action": result["action"],
        "status": result["status"],
        "timeframe": result["timeframe"],
        "sp_timeframe": result.get("sp_timeframe"),  # Optional, helpful for debugging
    }

    print(f"📤 Broadcasting Single Print: {message} to {len(connected_clients)} clients")

    for client in connected_clients.copy():
        try:
            await client.send_json(message)
        except Exception as e:
            connected_clients.discard(client)
            print(f"❌ Removed client due to error: {e}")



async def broadcast_random_counter():
    counter = 0
    while True:
        if connected_clients:
            message = {
                "type": "random_counter",
                "counter": counter,
                "randomValue": random.randint(1, 100)
            }
            print(f"📤 Broadcasting Random Counter: {message} to {len(connected_clients)} clients")
            for client in connected_clients.copy():
                try:
                    await client.send_json(message)
                except Exception as e:
                    connected_clients.discard(client)
                    print(f"❌ Removed client due to error: {e}")
        counter += 1
        await asyncio.sleep(5)  # broadcast every 5 seconds