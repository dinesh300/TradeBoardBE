from typing import List
from fastapi import WebSocket

connected_clients: List[WebSocket] = []

async def broadcast_trade_update(ticker: str, price: float):
    message = {"symbol": ticker, "lastTradePrice": price}
    print(f"📤 Broadcasting: {message}")
    for client in connected_clients[:]:
        try:
            await client.send_json(message)
        except Exception as e:
            connected_clients.remove(client)
            print(f"❌ Removed client due to error: {e}")
