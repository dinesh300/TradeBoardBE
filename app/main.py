# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asyncio import sleep
from app.routes import anomaly_entry_routes, subscribed_routes
from app.accelpix_service import start_accelpix_loop
import asyncio
from fastapi import  WebSocket
from fastapi import WebSocketDisconnect
from app.ws_manager import connected_clients
from fastapi import FastAPI
from app.routes import subscribed_routes, anomaly_ticker_routes, anomaly_entry_routes


app = FastAPI()
origins = ["http://localhost:3000","https://courageous-medovik-a4968d.netlify.app"]
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#init_db()
# Routers
app.include_router(subscribed_routes.router)
app.include_router(anomaly_ticker_routes.router)
app.include_router(anomaly_entry_routes.router)


@app.on_event("startup")
async def startup():
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
            try:
                await websocket.receive_text()  # Or implement ping/pong logic here
            except asyncio.TimeoutError:
                break
            await sleep(5)
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    finally:
        connected_clients.discard(websocket)


