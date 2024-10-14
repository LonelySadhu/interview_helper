import os
import asyncio
import openai
import time
from fastapi import FastAPI, WebSocket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
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
            
            # Интеграция с OpenAI ассистентом
            assistant_response = await get_assistant_response(data)
            
            # Отправляем ответ клиенту
            await manager.send_message(assistant_response)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        manager.disconnect(websocket)

# Функция для отправки запроса ассистенту и получения ответа
async def get_assistant_response(user_input: str) -> str:
    thread, run = create_thread_and_run(user_input)
    run = wait_on_run(run, thread)
    response = get_response(thread)
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
    thread = client.beta.threads.create()
    run = submit_message(assistant_id, thread, user_input)
    return thread, run


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5) 
    return run

def format_response(messages):
    # Форматируем текстовый ответ для отправки через WebSocket
    # Фильтруем только сообщения ассистента
    assistant_messages = [
        msg.content[0].text.value for msg in messages if msg.role == "assistant"
    ]

    # Объединяем сообщения ассистента в один ответ
    assistant_response = "\n".join(assistant_messages)
    return assistant_response

# Класс для отслеживания появления новых файлов
class TextFileHandler(FileSystemEventHandler):
    def __init__(self, folder_path: str, websocket_manager: WebSocketManager):
        self.folder_path = folder_path
        self.websocket_manager = websocket_manager  # Добавляем менеджер WebSocket

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".txt"):
            logger.info(f"Новый файл обнаружен: {event.src_path}")
            
            # Создаем новый цикл событий для текущего потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем обработку файла в новом цикле
            loop.run_until_complete(self.process_new_file(event.src_path))

    async def process_new_file(self, file_path: str):
        # Чтение содержимого файла
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

            # Отправляем содержимое файла ассистенту
            assistant_response = await get_assistant_response(file_content)

            # Логируем или обрабатываем ответ ассистента
            logger.info("Ответ ассистента:", assistant_response)

            # Отправляем ответ ассистента клиентам WebSocket
            await self.websocket_manager.send_message(assistant_response)


# Функция для запуска наблюдателя за папкой
def start_watching(folder_path: str, manager: WebSocketManager):
    event_handler = TextFileHandler(folder_path, manager)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    return observer

# Запуск FastAPI и отслеживание изменений в папке

folder_to_watch = "./transcriptions"  # Папка для отслеживания
os.makedirs(folder_to_watch, exist_ok=True)

# Создаем WebSocketManager
manager = WebSocketManager()

# Запускаем наблюдение за файлами и передаем менеджер WebSocket
observer = start_watching(folder_to_watch, manager)


try:
    import uvicorn
    logger.info("Uvicorn starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
finally:
    observer.stop()
    observer.join()
