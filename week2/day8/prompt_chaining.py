import os
from time import sleep
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq api key not found!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

JD="""
We are hiring a Backend Python Developer.

Requirements:
- Strong Python
- FastAPI or Django
- React
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years of experience
"""

RESUME="""
Name: Rahul Sharma

Experience:
3 years as a Software Developer.

Skills:
Python, FastAPI, MySQL, Docker, AI tools, Java, MERN
REST APIs, Git

Projects:
Built a food delivery backend using
FastAPI and MySQL.

Deployed applications using Docker.
"""

# General function to call the LLM
def call_llm(system_prompt, user_prompt):
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    response=client.chat.completions.create(messages=messages, model=model)
    answer=response.choices[0].message.content
    return answer

# Function to extract the skills and experiences from the Resume
def extract_resume():
    system_prompt=f"""
    You are an expert hr assistant. 
    #TASK
    your task is to extract all the skills and experiences form the resume
    - do not invent skills
    - extract exact skills mentioned in the resume skills section
    - if skills mentioned in commonly used short form then consider them. for example MERN -> means candidate has knowledge on Mongodb, React, Express and Node
    - do not invent experiences
    - go through from the experiences then extract the domain and the duration. for example 3 years+ SDE -> means candidate has more than 3 years experience as Software Developer Engineer 
    """

    user_prompt=f"""
    Extract the resume skills and experiences {RESUME}
    """
    return call_llm(system_prompt, user_prompt)


# Function to extract the skills and experiences from the Job Description
def extract_JD():
    system_prompt=f"""
    You are an expert hr assistant. 
    #TASK
    your task is to extract all the skills and experiences form the Job description
    - do not invent skills
    - extract exact skills mentioned in the job description skills section
    - if skills mentioned in commonly used short form then consider them.
    - do not invent required experience
    - go through from the required experience then extract the domain and the duration. for example 3 years+ SDE -> means the job need 3 years or more than 3 years experience as Software Developer Engineer 
    """

    user_prompt=f"""
    Extract the jd skills and required experiences {JD}
    """
    return call_llm(system_prompt, user_prompt)

def compare_result(candidate, jd):
    system_prompt=f"""
    You are an expert hr assistant. 
    #TASK
    Your task is to compare the skills, experiences of candidate and the skills, experience required in the JD and produce a final score between
    1 and 100. also produce a short verdict whther the candidate is a good fit for the role.

    #OUTPUT FORMAT
    Matched:
    Unmatched:
    Final Score: score you have decided
    Verdict: why candidate selected / not selected
    """

    user_prompt=f"""
    compare the candidate resume {candidate} and the jd {jd}
    """
    return call_llm(system_prompt, user_prompt)

candidate=extract_resume()
print(candidate)
sleep(2)
jd=extract_JD()
print(jd)
sleep(2)
result=compare_result(candidate, jd)
print(result)