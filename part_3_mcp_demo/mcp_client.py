import sys
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = str(Path(__file__).resolve().parent / "mcp_server.py")


class MCPClient:
    def __init__(self):
        self.session = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=sys.executable, args=[SERVER_SCRIPT]
        )
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()

    async def get_tools(self):
        return await self.session.list_tools()

    async def call_tool(self, name, arguments):
        return await self.session.call_tool(name, arguments)

    async def close(self):
        await self._exit_stack.aclose()
