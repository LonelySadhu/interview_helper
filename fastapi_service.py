import asyncio
from fastapi import FastAPI, WebSocket, Request
from ws_manager import WebSocketManager
from logger import logger

app = FastAPI()

# Initialization of WebSocket manager
manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(2)  # waiting to maintain the connection
    except Exception as e:
        logger.error(f"Error WebSocket: {e}")
    finally:
        await manager.disconnect(websocket)

@app.post("/send_response")
async def send_response(request: Request):
    # Getting the assistant's response from a POST request
    data = await request.json()
    assistant_response = data.get("response")
    logger.info(f"Assistant response received: {assistant_response}")

    # Send a response via WebSocket to all connected clients
    await manager.broadcast(assistant_response)

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
