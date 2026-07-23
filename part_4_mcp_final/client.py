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


class IncidentAssistantClient:
    """Async wrapper around the incident-assistant MCP server and its Agent."""

    def __init__(self, model: str | None = None):
        self.model = model
        self.server = MCPServerStdio(
            name="incident-assistant",
            params={"command": sys.executable, "args": [SERVER_SCRIPT]},
        )
        self.agent: Agent | None = None

    async def __aenter__(self) -> "IncidentAssistantClient":
        await self.server.__aenter__()
        self.agent = Agent(
            name="Incident Assistant",
            instructions=INSTRUCTIONS,
            model=self.model,
            mcp_servers=[self.server],
        )
        return self

    async def __aexit__(self, *exc_info):
        await self.server.__aexit__(*exc_info)

    async def ask(self, question: str) -> str:
        """Run a question to completion and return the final answer text."""
        result = await Runner.run(self.agent, question)
        return result.final_output

    def run_streamed(self, question: str):
        """Run a question and return a streaming result (see Runner.run_streamed)."""
        return Runner.run_streamed(self.agent, question)
