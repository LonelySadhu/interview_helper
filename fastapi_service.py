import asyncio
from fastapi import FastAPI, WebSocket, Request
from ws_manager import WebSocketManager
from logger import logger

app = FastAPI()

# Инициализация менеджера WebSocket
manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(2)  # Простое ожидание для поддержания соединения
    except Exception as e:
        logger.error(f"Ошибка WebSocket: {e}")
    finally:
        await manager.disconnect(websocket)

@app.post("/send_response")
async def send_response(request: Request):
    # Получаем ответ ассистента из POST-запроса
    data = await request.json()
    assistant_response = data.get("response")
    logger.info(f"Получен ответ ассистента: {assistant_response}")

    # Отправляем ответ через WebSocket всем подключённым клиентам
    await manager.broadcast(assistant_response)

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
