import os
import asyncio
import openai
from fastapi import FastAPI, WebSocket
from pathlib import Path
from ws_manager import WebSocketManager
from logger import logger
from settings import settings

# Конфигурация API ключа OpenAI
openai.api_key = settings.api_key
assistant_id = settings.assistant_id

client = openai.OpenAI(api_key=openai.api_key)

# Инициализация FastAPI приложения
app = FastAPI()

# Инициализация менеджера WebSocket
manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            assistant_response = await get_assistant_response(data)
            await manager.send_message(assistant_response)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await manager.disconnect(websocket)

# Асинхронная функция для отправки запроса ассистенту и получения ответа
async def get_assistant_response(user_input: str) -> str:
    thread, run = create_thread_and_run(user_input)  # убрали await, если это синхронные методы
    run = wait_on_run(run, thread)  # убрали await
    response = get_response(thread)  # убрали await
    return format_response(response)

# Вспомогательные функции для взаимодействия с OpenAI
def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()  # синхронный вызов
    run = submit_message(assistant_id, thread, user_input)  # синхронный вызов
    return thread, run

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)  # синхронный вызов
    return run

def format_response(messages):
    assistant_messages = [
        msg.content[0].text.value for msg in messages if msg.role == "assistant"
    ]
    assistant_response = "\n".join(assistant_messages)
    return assistant_response

# Асинхронная функция для периодической проверки директории на новые файлы
async def check_for_new_files(folder_path: str, websocket_manager: WebSocketManager):
    processed_files = set()  # Набор для хранения уже обработанных файлов
    folder = Path(folder_path)
    
    while True:
        txt_files = {f for f in folder.iterdir() if f.is_file() and f.suffix == ".txt"}
        new_files = txt_files - processed_files
        
        for file_path in new_files:
            logger.info(f"Новый файл обнаружен: {file_path}")
            await process_new_file(file_path, websocket_manager)
            processed_files.add(file_path)
        
        await asyncio.sleep(2)

# Асинхронная функция для обработки новых файлов
async def process_new_file(file_path: Path, websocket_manager: WebSocketManager):
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        assistant_response = await get_assistant_response(file_content)
        logger.info(f"Ответ ассистента: {assistant_response}")
        await websocket_manager.send_message(assistant_response)

# Асинхронная функция для запуска FastAPI сервера и проверки файлов
async def run_server_and_check_files():
    # Запуск проверки файлов в отдельной задаче
    folder_to_watch = "./transcriptions"
    os.makedirs(folder_to_watch, exist_ok=True)

    manager = WebSocketManager()
    
    # Запускаем проверку новых файлов
    file_check_task = asyncio.create_task(check_for_new_files(folder_to_watch, manager))

    # Запускаем FastAPI сервер
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    
    # Запуск сервера и задачи параллельно
    await asyncio.gather(server.serve(), file_check_task)

# Запуск основного цикла событий
if __name__ == "__main__":
    asyncio.run(run_server_and_check_files())
