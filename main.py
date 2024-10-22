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
        log_func(line.decode('utf-8', errors='replace').strip())  # Handling decoding error
    process.stdout.close()

def log_error(process, log_func):
    for line in iter(process.stderr.readline, b''):
        log_func(line.decode('utf-8', errors='replace').strip())  # Handling decoding error
    process.stderr.close()

transcribe_model = "poetry run python transcriber_service.py"
logger.info("Model loading...")
p1 = run_program(transcribe_model)

# Starting threads for output logging
threading.Thread(target=log_output, args=(p1, logger.info)).start()
threading.Thread(target=log_error, args=(p1, logger.error)).start()

# Waiting 2 minutes to load the model
time.sleep(120)
logger.info("Model loaded, services running...")

assistant = "poetry run python assistant_service.py"
fastapi = "poetry run python fastapi_service.py"
audio_service = "poetry run python recorder_service.py"
p2 = run_program(fastapi)
threading.Thread(target=log_output, args=(p2, logger.info)).start()
threading.Thread(target=log_error, args=(p2, logger.error)).start()
logger.info("Fastapi running...")

p3 = run_program(assistant)
threading.Thread(target=log_output, args=(p3, logger.info)).start()
threading.Thread(target=log_error, args=(p3, logger.error)).start()
logger.info("AI assistant running...")

p4 = run_program(audio_service)
threading.Thread(target=log_output, args=(p4, logger.info)).start()
threading.Thread(target=log_error, args=(p4, logger.error)).start()
logger.info("Recording...")
logger.info("Open index.html in your browser")

try:
    # Main process
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logger.error("All processes is closing...")

    # Terminate all child processes
    p1.terminate()
    p2.terminate()
    p3.terminate()

   
    p1.wait()
    p2.wait()
    p3.wait()

    logger.info("Bye!")
    sys.exit(0)
