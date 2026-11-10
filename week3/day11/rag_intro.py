import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq api key not found!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

knowledge_base={
    "soap": "virat uses dettol soap.",
    "perfume": "virat uses aux perfume"
}

def retrieve_context(question):
    question=question.lower()
    if "soap" in question:
        return knowledge_base["soap"]
    elif "perfume" in question:
        return knowledge_base["perfume"]
    else:
        return None

def ask_llm(question):
    context=retrieve_context(question)
    system_prompt=f"""Give answer in single line. answer only based on the context, do not invent things from your own. context: {context}"""
    system_message={
        "role": "system",
        "content": system_prompt
    }
    user_message={
        "role": "user",
        "content": question
    }
    messages=[system_message, user_message]
    response=client.chat.completions.create(messages=messages, model=model)
    ans=response.choices[0].message.content
    return ans

question1="what soap virat kohli use?"
question2="what fragrance virat kohli use?"
print(ask_llm(question1))



