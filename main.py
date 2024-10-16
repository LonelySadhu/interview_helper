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
logger.info("Модель загружена, запускаем сервисы...")
assistant = "poetry run python assistant_service_v2.py"
fastapi = "poetry run python fastapi_service.py"
audio_service = "poetry run python recorder_service.py"
p2 = run_program(fastapi)
p3 = run_program(assistant)
p4 = run_program(audio_service)
logger.info("Запись...")
logger.info("Откройте браузером файл index.html")

try:
    # Основной процесс
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logger.error("Завершение программ...")

    # Завершаем все дочерние процессы
    p1.terminate()
    p2.terminate()
    p3.terminate()

    # Ждем завершения всех программ
    p1.wait()
    p2.wait()
    p3.wait()

    logger.info("Все процессы завершены.")
    sys.exit(0)
