from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
llm_model = "gpt-5.4-nano"
llm_message = "Welcome all learners to this foundation level program on AI, Agents and MCP in less than 100 words."

client = OpenAI()
response = client.responses.create(model=llm_model, input=llm_message)

print(response.output_text)
