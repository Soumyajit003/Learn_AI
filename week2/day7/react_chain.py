import os
from time import sleep
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq api key not found!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

# function/tools definations
def get_population(city):
    city=city.strip().lower()
    populations = {
        "hyderabad": 400000,
        "kolkata": 500000,
        "delhi": 300000
    }
    return populations.get(city, "City not found!!!")

# def calculate(expr):
#     try:
#         return eval(expr)
#     except:
#         return "calculation error!!!"

import ast
import operator

def calculate(expr):
    try:
        return eval(expr)
    except:
        return "calc error!"


# defining the tools
tools={
    "get_population": get_population,
    "calculate": calculate
}

# **writing the system prompt
system_prompt = """
You are an AI agent following the ReAct framework.

You have access to these tools:

1. get_population(city)
   Returns the population of a city.

2. calculate(expr)
   Performs mathematical calculations.

IMPORTANT RULES:

1. Follow the Thought -> Action -> Observation cycle.

2. Call only ONE tool per response.

3. Never generate an Observation yourself.
   Only Python provides observations.

4. Never invent, modify, or guess tool results.

5. Always use the exact values returned by tools.

6. Wait for an Observation before taking the next action.

7. Never call a tool that is not available.

8. If you need information from multiple tools,
   call them one at a time.

9. Use the calculate tool for mathematical operations.

10. When the task is complete, provide the Final Result.

ACTION FORMAT:

Thought: Explain what you need to do.

Action: get_population("kolkata")

OR

Action: calculate("400000 + 500000")

IMPORTANT:
Generate exactly ONE Action per response.
Do not generate multiple actions.

FINAL RESPONSE FORMAT:

Final Result: Your answer

Do not generate Action and Final Result together.
"""

# functionality of the agent
def run_agent(question):
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for step in range(10):
        print("\n--------------")
        print("STEP: ", step+1)
        print("--------------")

        response=client.chat.completions.create(model=model, messages=messages, temperature=0)
        answer=response.choices[0].message.content
        print(answer)       # in answer llm will give the thought and action

        if "Final Result:" in answer:
            break

        # Finding the action
        action=re.search(
            r"Action:\s*(\w+)\((.*?)\)",
            answer
        )

        if action:
            tool_name=action.group(1)
            tool_input=action.group(2)
            tool_input=tool_input.strip()
            tool_input=tool_input.strip('"')

            # lets run the tool and get the output of the tool
            if tool_name in tools:
                tool=tools[tool_name]
                observation=tool(tool_input)
            else:
                observation="Tool not found!!!"

            print("Observation: ", observation)

            # adding the response to the LLM memory
            messages.append({
                "role": "assistant",
                "content": answer
            })

            # giving tool result back to the LLM for further reson+act
            messages.append({
                "role": "user",
                "content": "Observation: "+str(observation)
            })

        sleep(5)

# def run_agent(question):

#     messages = [
#         {
#             "role": "system",
#             "content": system_prompt
#         },
#         {
#             "role": "user",
#             "content": question
#         }
#     ]

#     for step in range(10):

#         print("\n----------------")
#         print("STEP:", step + 1)
#         print("----------------")

#         response = client.chat.completions.create(
#             model=model,
#             messages=messages,
#             temperature=0
#         )

#         answer = response.choices[0].message.content or ""

#         print("LLM:", answer)

#         # Find action lines
#         actions = re.findall(
#             r'(?m)^\s*Action:\s*(\w+)\("([^"\n]*)"\)\s*$',
#             answer
#         )

#         # Check whether the agent has finished
#         if "Final Result:" in answer and len(actions) == 0:

#             print("\nAgent completed!")
#             break

#         # Validate action count
#         if len(actions) != 1:

#             messages.append({
#                 "role": "assistant",
#                 "content": answer
#             })

#             messages.append({
#                 "role": "user",
#                 "content": (
#                     "Observation: Invalid response. "
#                     "Generate exactly one valid Action line "
#                     "or provide Final Result."
#                 )
#             })

#             continue

#         # Extract tool name and input
#         tool_name, tool_input = actions[0]

#         print("Tool:", tool_name)
#         print("Input:", tool_input)

#         # Execute tool
#         if tool_name in tools:

#             try:
#                 tool = tools[tool_name]
#                 observation = tool(tool_input)

#             except Exception as e:
#                 observation = f"Tool execution failed: {e}"

#         else:
#             observation = "Tool not found!"

#         print("Observation:", observation)

#         # Save assistant response
#         messages.append({
#             "role": "assistant",
#             "content": answer
#         })

#         # Return observation to LLM
#         messages.append({
#             "role": "user",
#             "content": f"Observation: {observation}"
#         })

#         sleep(2)

#     else:
#         print("Maximum iterations reached!")

prompt="""
I am soumyajit. I want to find the total population of city hyderabad and kolkata. Help me with this.
"""
run_agent(prompt)



