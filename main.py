import subprocess
import time
import signal
import sys
from logger import logger

def run_program(command):
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

transcribe_model = "poetry run python transcriber_service.py"  
p1 = run_program(transcribe_model)

# Ожидание 2 минуты для загрузки модели
time.sleep(120)
logger.info("Модель загружена, можем записывать звук...")
audio_service = "poetry run python recorder_service.py"
logger.info("Запись...")  
assistant = "poetry run python assistant_service.py"   
logger.info("Откройте браузером файл index.html")
p2 = run_program(audio_service)
p3 = run_program(assistant)

try:
    # Основной процесс 
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logger.error("Завершение программ...")

    # Посылаем сигнал SIGINT (Ctrl+C) всем дочерним процессам
    p1.send_signal(signal.SIGINT)
    p2.send_signal(signal.SIGINT)
    p3.send_signal(signal.SIGINT)

    # Ждем завершения всех программ
    p1.wait()
    p2.wait()
    p3.wait()

    logger.info("Все процессы завершены.")
    sys.exit(0)
