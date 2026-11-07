import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq api key not found!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

message={
    "role": "user",
    "content": "Explain AI."
}

messages=[message]

response=client.chat.completions.create(model=model, messages=messages, stream=True)

for chunk in response:
    content=chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)