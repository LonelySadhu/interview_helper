import subprocess
import time
import signal
import sys
import threading
from logger import logger

def run_program(command):
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def log_output(process, log_func):
    for line in iter(process.stdout.readline, b''):
        log_func(line.decode('utf-8', errors='replace').strip())  # Обрабатываем ошибку декодирования
    process.stdout.close()

def log_error(process, log_func):
    for line in iter(process.stderr.readline, b''):
        log_func(line.decode('utf-8', errors='replace').strip())  # Обрабатываем ошибку декодирования
    process.stderr.close()

transcribe_model = "poetry run python transcriber_service.py"
p1 = run_program(transcribe_model)

# Запуск потоков для логирования вывода
threading.Thread(target=log_output, args=(p1, logger.info)).start()
threading.Thread(target=log_error, args=(p1, logger.error)).start()

# Ожидание 2 минуты для загрузки модели
time.sleep(120)
logger.info("Модель загружена, запускаем сервисы...")

assistant = "poetry run python assistant_service.py"
fastapi = "poetry run python fastapi_service.py"
audio_service = "poetry run python recorder_service.py"
p2 = run_program(fastapi)
threading.Thread(target=log_output, args=(p2, logger.info)).start()
threading.Thread(target=log_error, args=(p2, logger.error)).start()
logger.info("Fastapi сервис запущен...")

p3 = run_program(assistant)
threading.Thread(target=log_output, args=(p3, logger.info)).start()
threading.Thread(target=log_error, args=(p3, logger.error)).start()
logger.info("Ассистент запущен...")

p4 = run_program(audio_service)
threading.Thread(target=log_output, args=(p4, logger.info)).start()
threading.Thread(target=log_error, args=(p4, logger.error)).start()
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
