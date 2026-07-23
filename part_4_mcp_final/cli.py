import asyncio
import os
import sys

from client import IncidentAssistantClient


async def main():
    async with IncidentAssistantClient() as client:
        print("AI Incident Assistant. Ask about an order (e.g. 'Why did order ORD-10234 fail and what should I do?'), or type 'exit' to quit.\n")
        while True:
            question = input("> ").strip()
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue
            answer = await client.ask(question)
            print(f"\n{answer}\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in part_4_mcp_final/.env before running (see .env.example).")
        sys.exit(1)
    asyncio.run(main())
