import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import numpy as np
import sys

load_dotenv()

model_emb=SentenceTransformer("all-MiniLM-L6-v2")

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("GROQ API key error!!!")

client=Groq(api_key=my_api_key)
model_groq="openai/gpt-oss-120b"

documents = [
    "Employees receive 24 days of paid leave per year.",
    "Employees work from the office on Tuesday, Wednesday and Thursday. "
    "Monday and Friday are optional work-from-home days.",
    "Employees receive Rs 3000 per month for gym reimbursement.",
    "Employees can claim Rs 2000 per month for home internet.",
    "Employees have a 90 day notice period."
]

embedded_document=model_emb.encode(documents)

def cosine_similarity(a, b):
    return np.dot(a, b)/(
        np.linalg.norm(a)*np.linalg.norm(b)
    )

def retrieve(question):
    embedded_question=model_emb.encode(question)
    scores=[]
    for i, document in enumerate(embedded_document):
        score=cosine_similarity(embedded_question, document)
        scores.append((score, documents[i]))
    scores.sort(reverse=True)
    # print(scores)
    return scores[0]

def ask_llm(question, context):
    system_prompt=f"""answer in one line only. Answer only based on this context. do not hallucinate. Context: {context}"""
    system_message={
        "role": "system",
        "content": system_prompt
    }
    user_message={
        "role": "user",
        "content": question
    }
    messages=[system_message, user_message]
    response=client.chat.completions.create(model=model_groq, messages=messages)
    return response.choices[0].message.content

question="how much money I can get for my fitness?"
context=retrieve(question)
print(context)
answer=ask_llm(question, context)
print(answer)