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

# 3 different prompts
prompt1="hello"
prompt2="who is spiderman?"
prompt3="write an essey about bmw in 1000 words."

prompts=[prompt1, prompt2, prompt3]

for prompt in prompts:
    message={
        "role":role,
        "content":prompt
    }
    messages=[message]
    # response=client.chat.completions.create(model=model, messages=messages)
    # usage=response.usage
    # print(f"Prompt: {prompt} --> your tokens: {usage.prompt_tokens} + completion tokes: {usage.completion_tokens} = total tokens used: {usage.total_tokens}")

    response=client.chat.completions.create(model=model, messages=messages, max_tokens=1000)
    usage=response.usage
    print(f"Prompt: {prompt} --> your tokens: {usage.prompt_tokens} + completion tokes: {usage.completion_tokens} = total tokens used: {usage.total_tokens} | Finish reason: {response.choices[0].finish_reason}")

