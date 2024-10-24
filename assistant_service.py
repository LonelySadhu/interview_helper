import os
import asyncio
import openai
import requests
import time 
from pathlib import Path
from logger import logger
from settings import settings

# OpenAI Key API
openai.api_key = settings.api_key
assistant_id = settings.assistant_id

client = openai.OpenAI(api_key=openai.api_key)

# Path to the directory for tracking
folder_to_watch = "./transcriptions"
os.makedirs(folder_to_watch, exist_ok=True)

#  FastAPI service URL for sending data
FASTAPI_URL = "http://localhost:8000/send_response"

async def check_for_new_files(folder_path: str):
    processed_files = set()  # Set for storing already processed files
    folder = Path(folder_path)
    
    while True:
        txt_files = {f for f in folder.iterdir() if f.is_file() and f.suffix == ".txt"}
        new_files = txt_files - processed_files
        
        for file_path in new_files:
            logger.info(f"New file detected: {file_path}")
            await process_new_file(file_path)
            processed_files.add(file_path)
        
        await asyncio.sleep(2)

async def process_new_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        assistant_response = await get_assistant_response(file_content)
        logger.info(f"Assistant response: {assistant_response}")

        # Send the assistant's response to the FastAPI service via HTTP request
        data = {"response": assistant_response}
        try:
            response = requests.post(FASTAPI_URL, json=data)
            response.raise_for_status()
            logger.info(f"Data successfully sent to FastAPI: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error when sending data: {e}")

# Asynchronous function for sending a request to the assistant and receiving a response
async def get_assistant_response(user_input: str) -> str:
    try:
        thread, run = create_thread_and_run(user_input)
        run = wait_on_run(run, thread)
        response = get_response(thread)
        return format_response(response)
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API Error: {e}")
        return "An error occurred while processing your request."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "An unexpected error occurred."

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    
    if not messages:
        raise ValueError(f"No messages found for thread {thread.id}")
    
    return messages

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    logger.info(f"Thread created with ID: {thread.id}")
    
    if not thread or not thread.id:
        raise ValueError("Thread was not created successfully.")
    
    run = submit_message(assistant_id, thread, user_input)
    logger.info(f"Run started for thread {thread.id} with run ID: {run.id}")
    
    return thread, run

def wait_on_run(run, thread):
    while run.status in ["queued", "in_progress"]:
        logger.info(f"Run status for thread {thread.id}: {run.status}")
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)  
    return run

def format_response(messages):
    assistant_messages = [
        msg.content[0].text.value for msg in messages if msg.role == "assistant"
    ]
    assistant_response = "\n".join(assistant_messages)
    return assistant_response


asyncio.run(check_for_new_files(folder_to_watch))
