import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Error during Groq API key!!!")

client=Groq(api_key=my_api_key)

role="user"
model="openai/gpt-oss-120b"

# customer raised email
customer_email="Hello my name is Soumyajit Bera. I am from kolkata. I am a gamer.I brougth an ps5 to play games and stream on youtube. but I am facing an issue, the ps5 is not responding when trying to open games sometimes, and also shuting down. that's why I am contacting. You can reach out in this email soumya.bera@gmail.com. Thankyou."

# creating the structure for specific output
class Ticket(BaseModel):
    name:str
    email:str
    issue:str

schema=Ticket.model_json_schema()

response_format={
    "type":"json_object"
}

system_prompt=f"""
Extract personal information from the ticket strictly based on the schema and give a json output.{schema}
"""
message_system={
    "role":"system",
    "content":system_prompt
}

user_prompt=f"""
This is a customer ticket. Please extract the personal information from this.{customer_email}
"""
message_user={
    "role":role,
    "content":user_prompt
}

messages=[message_system, message_user]

response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)

answer=response.choices[0].message.content
print(answer)



# reading the json file
import json
raw_json=answer
data_file=json.loads(raw_json)
ticket=Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.issue)