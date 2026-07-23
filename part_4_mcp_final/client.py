import asyncio
import os
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

SERVER_SCRIPT = str(HERE / "server.py")

INSTRUCTIONS = """
You are a production incident investigator. When an engineer asks why an
order failed, investigate methodically using the available tools:

1. Call get_order to find the order's status, service, and error.
2. Call search_logs with the order_id to see what happened around the
   failure.
3. Call latest_deployment with the order's service to check whether a
   recent deployment could be the cause.
4. Call similar_incidents with the exact error value returned by
   get_order, verbatim, to check whether this has happened before and how
   it was resolved.

Then produce a concise root cause analysis: what failed, why (tying it to
the deployment if relevant), and what the engineer should do next (citing
the past incident's resolution if one was found).
"""


async def main():
    async with MCPServerStdio(
        name="incident-assistant",
        params={"command": sys.executable, "args": [SERVER_SCRIPT]},
    ) as server:
        agent = Agent(
            name="Incident Assistant",
            instructions=INSTRUCTIONS,
            mcp_servers=[server],
        )

        print("AI Incident Assistant. Ask about an order (e.g. 'Why did order ORD-10234 fail and what should I do?'), or type 'exit' to quit.\n")
        while True:
            question = input("> ").strip()
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue
            result = await Runner.run(agent, question)
            print(f"\n{result.final_output}\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in part_4_mcp_final/.env before running (see .env.example).")
        sys.exit(1)
    asyncio.run(main())
