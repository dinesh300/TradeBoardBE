from accelpix_service import start_accelpix
from anomalies_api import router as anomalies_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
from ws_manager import connected_clients


app = FastAPI()
app.include_router(anomalies_router)

origins = ["http://localhost:3000","https://courageous-medovik-a4968d.netlify.app/"]

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
    #asyncio.create_task(simulate_day_open_broadcast())  # ✅ Start simulation



@app.get("/")
def health():
    return {"status": "running"}

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




