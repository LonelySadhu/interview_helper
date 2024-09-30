import os
import asyncio
import openai
from fastapi import FastAPI, WebSocket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ������������ API ����� OpenAI
openai.api_key = "���-����-openai"

# ������������� FastAPI ����������
app = FastAPI()

# WebSocket ���������� ��� ������� � ��������
class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# ������������� ��������� WebSocket
manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(f"�� ���������: {data}")
    except Exception as e:
        print(f"������: {e}")
    finally:
        manager.disconnect(websocket)

# ����� ��� ������������ ��������� ����� ������
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".txt"):
            print(f"����� ���� ���������: {event.src_path}")
            asyncio.create_task(self.process_new_file(event.src_path))

    async def process_new_file(self, file_path: str):
        # ������ ����������� �����
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # �������� ����������� ����� � OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": file_content}],
            stream=True  # �������� ������
        )

        async for chunk in response:
            if chunk.get("choices"):
                message_chunk = chunk["choices"][0]["delta"].get("content", "")
                if message_chunk:
                    # �������� ������ ����� ������ �� WebSocket
                    await manager.send_message(message_chunk)

# ������� ��� ������� ����������� �� ������
def start_watching(folder_path: str):
    event_handler = NewFileHandler(folder_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    return observer

# ������ FastAPI � ������������ ��������� � �����
if __name__ == "__main__":
    folder_to_watch = "./watched_folder"  # ����� ��� ������������
    os.makedirs(folder_to_watch, exist_ok=True)

    observer = start_watching(folder_to_watch)

    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        observer.stop()
        observer.join()
