from accelpix_service import start_accelpix
from anomalies_api import router as anomalies_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
import asyncio
from ws_manager import connected_clients, broadcast_trade_update

app = FastAPI()
app.include_router(anomalies_router)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await start_accelpix()
    #asyncio.create_task(broadcast_counter())  # Start broadcasting
    asyncio.create_task(broadcast_trade_update("TCS-1", 3500))


@app.get("/")
def health():
    return {"status": "running"}

@app.websocket("/ws/trades")
async def trade_websocket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception as e:
        print("WebSocket closed:", e)
        connected_clients.remove(websocket)
