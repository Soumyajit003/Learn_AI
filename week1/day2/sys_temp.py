import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("GROQ API key error!!!")

client=Groq(api_key=my_api_key)
role="user"
model="openai/gpt-oss-120b"
prompt="what is llm"

system_message={
    "role":"system",
    "content":"you are a friendly ai tutor, explain in simple words"
}

my_message={
    "role":role,
    "content":prompt
}

messages=[system_message, my_message]

response=client.chat.completions.create(model=model, messages=messages, temperature=0)
answer=response.choices[0].message.content
print(answer)