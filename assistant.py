
from openai import OpenAI

api_key = "sk-NLehN06vh8OrgGzDdA_5VGJ8pQQYNAcQ7Y-fYDXzWOT3BlbkFJcpJtnXcG1LsZd2Ou-3uDVPSz5xbuGkzc_A0_Z4iqAA"


assistant_id = "asst_omGvcxwgcDJoCo81Q8E4a6AK"


user_input = "Привет! Можешь рассказать мне о своем функционале?"

client = OpenAI(api_key=api_key)
assistant = client.beta.assistants.retrieve(assistant_id)

print(assistant)
