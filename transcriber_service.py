import asyncio
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from transcriber_async import Transcriber
from logger import logger

# A class for tracking the appearance of new files
class AudioFileHandler(FileSystemEventHandler):
    def __init__(self, folder_path: str, folder_output: str, loop):
        self.folder_path = folder_path
        self.folder_output = folder_output
        self.loop = loop
        self.transcriber = Transcriber('model')

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".wav"):
            logger.info(f"New file detected: {event.src_path}")
            asyncio.run_coroutine_threadsafe(self.transcriber.write_transcription_to_file(event.src_path,
                                                                          self.folder_output),
                                                                          self.loop)



def start_watching(folder_path: str, folder_output: str, loop):
    event_handler = AudioFileHandler(folder_path, folder_output, loop)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    return observer

async def main():
    folder_to_watch = "./recorders"  # Tracking folder
    folder_output = "./transcriptions"  # Folder for saving text”
    os.makedirs(folder_to_watch, exist_ok=True)
    os.makedirs(folder_output, exist_ok=True)

    loop = asyncio.get_running_loop()
    observer = start_watching(folder_to_watch, folder_output, loop)

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()

    
asyncio.run(main())