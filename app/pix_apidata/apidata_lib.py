import asyncio
import json
import websockets

class ApiData:
    def __init__(self):
        self._ws = None
        self._on_connected = None
        self._on_disconnected = None
        self._on_trade_update = None

    def on_connection_started(self, callback):
        self._on_connected = callback

    def on_connection_stopped(self, callback):
        self._on_disconnected = callback

    def on_trade_update(self, callback):
        self._on_trade_update = callback

    async def initialize(self, token, host):
        url = f"wss://{host}/streaming?token={token}"
        try:
            print(f"🔐 Connecting to {url} ...")
            self._ws = await websockets.connect(url)
            print("🔐 Accelpix initialized")
            if self._on_connected:
                self._on_connected()
            asyncio.create_task(self._listen())
        except Exception as e:
            print("❌ WebSocket connection failed:", e)
            if self._on_disconnected:
                self._on_disconnected()

    async def _listen(self):
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    if self._on_trade_update:
                        self._on_trade_update(data)
                except Exception as e:
                    print("❌ Failed to parse message:", e)
        except Exception as e:
            print("❌ Error in WebSocket listening:", e)
            if self._on_disconnected:
                self._on_disconnected()

    async def subscribeAll(self, symbols):
        try:
            if not self._ws or self._ws.closed:
                raise RuntimeError("WebSocket not connected or closed")

            for symbol in symbols:
                subscribe_msg = {
                    "action": "subscribe",
                    "symbol": symbol
                }
                await self._ws.send(json.dumps(subscribe_msg))
            print(f"📡 Subscribed to: {symbols}")

        except Exception as e:
            print("❌ Failed to subscribe to symbols:", e)
