# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import anomaly, subscribe
from app.accelpix_service import start_accelpix_loop
import asyncio
from fastapi import  WebSocket
from fastapi import WebSocketDisconnect
from app.ws_manager import connected_clients
from app.database import init_db

app = FastAPI()
origins = ["http://localhost:3000","https://courageous-medovik-a4968d.netlify.app"]
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(anomaly.router)
app.include_router(subscribe.router)

@app.on_event("startup")
async def startup():
    init_db()
    # Start the Accelpix service loop as a background task
    asyncio.create_task(start_accelpix_loop())

@app.get("/")
async def root():
    return {"message": "Backend running with Accelpix service"}

@app.websocket("/ws/trades")
async def trade_websocket(websocket: WebSocket):
    try:
        await websocket.accept()
        connected_clients.add(websocket)
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.discard(websocket)

