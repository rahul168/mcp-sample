from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
llm_model = "gpt-5.4-nano"
llm_message = "Welcome all learners to this foundation level program on AI, Agents and MCP in less than 100 words."

def prepare_message(request):
    return [ { "role": "user", "content": request } ]

def get_response(response):
    return response.choices[0].message.content

client = OpenAI()
response = client.chat.completions.create(model=llm_model, messages=prepare_message(llm_message))

print(get_response(response))
