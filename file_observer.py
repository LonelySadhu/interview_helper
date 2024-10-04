import asyncio
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Класс для отслеживания появления новых файлов
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, folder_path: str, loop):
        self.folder_path = folder_path
        self.loop = loop

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".wav"):
            print(f"Новый файл обнаружен: {event.src_path}")
            asyncio.run_coroutine_threadsafe(self.file_handler(event.src_path), self.loop)

    async def file_handler(self, file_path: str):
        print(f"Executing file: {file_path}")

def start_watching(folder_path: str, loop):
    event_handler = NewFileHandler(folder_path, loop)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    return observer

async def main():
    folder_to_watch = "./recorders"  # Папка для отслеживания
    os.makedirs(folder_to_watch, exist_ok=True)

    loop = asyncio.get_running_loop()
    observer = start_watching(folder_to_watch, loop)

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    asyncio.run(main())