import openai
from openai import OpenAI
import time

api_key = "sk-NLehN06vh8OrgGzDdA_5VGJ8pQQYNAcQ7Y-fYDXzWOT3BlbkFJcpJtnXcG1LsZd2Ou-3uDVPSz5xbuGkzc_A0_Z4iqAA"
assistant_id = "asst_omGvcxwgcDJoCo81Q8E4a6AK"


user_input = "Привет! Можешь рассказать о своем функционале?"

client = OpenAI(api_key=api_key)

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


# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5) 
    return run

if __name__ == "__main__":
    thread, run = create_thread_and_run(user_input)
    run = wait_on_run(run, thread)
    pretty_print(get_response(thread))