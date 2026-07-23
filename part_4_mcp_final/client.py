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
You are an experienced Site Reliability Engineer.
Your job is to investigate production incidents.
Always think step by step.

Whenever information is available through MCP tools,
use those tools instead of guessing.

For failed orders:
1. Retrieve order details.
2. Retrieve application logs.
3. Check deployment history.
4. Search historical incidents.
5. Produce a Root Cause Analysis.

Your report must contain
• Summary
• Evidence
• Root Cause
• Recommended Actions
• Confidence Level

Never fabricate information.
"""

def create_mcp_server() -> MCPServerStdio:
    """Build the (not-yet-connected) MCP server for the incident-assistant tools."""
    return MCPServerStdio(
        name="incident-assistant",
        params={"command": sys.executable, "args": [SERVER_SCRIPT]},
    )


def create_agent(server: MCPServerStdio, model: str | None = None) -> Agent:
    """Build the incident-investigator Agent wired to a connected MCP server."""
    return Agent(
        name="Incident Assistant",
        instructions=INSTRUCTIONS,
        model=model,
        mcp_servers=[server],
    )


async def main():
    async with create_mcp_server() as server:
        agent = create_agent(server)

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
