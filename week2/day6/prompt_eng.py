import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq api key not found!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

user_email_1="""
Hello I am Surya. I love to eat momo. I want to buy a jet.
"""
user_email_2="""
Hello I am Surya. My brother want to join cse. what is the ending date of the course.
"""
user_email_3="""
I want to buy BMW.
"""
user_email_4="""
how many shops are there in the college campus.
"""

def call_llm(prompt):
    message={
        "role": "user",
        "content": prompt
    }
    messages=[message]
    response=client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content
    

bad_prompt=f"""
you are an institute counselor.
analyze the email.{user_email_1}
"""

good_prompt=f"""
#ROLE
    you a counselor in an University.
#TASK
    your task is to classify the student query/queries
#CONSTRAINT
    you have to classify the query in one of the three categories -> admission, course, placement, general
    if they are asking single query the category output will be also single, like -> admission
    if they are asking multiple quries the categories output will be also multiple, like -> admission, course
    do not invent categories
#INPUT DATA
    this is the user email{user_email_4}
#OUTPUT FORMAT
    the output should be only categories from the provided
    example: [for single - admission], [for multiple - course, placement]

#FEWSHOT
    example1: the email is about they are asking about they want to join Nursing course - category-> admission
    example2: they are asking about what is the duration of the course and what is the last date of admission - category-> course, admission
#FALLBACK
    if the email is not related to the provided categories then answer should be - "Sorry! I can't help you with this issue."
"""

print(call_llm(good_prompt))