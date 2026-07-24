import asyncio

from mcp_client import MCPClient


async def main():
    client = MCPClient()
    try:
        await client.connect()
        tools = await client.get_tools()
        print("\nAvailable MCP Tools")
        for tool in tools.tools:
            print(tool.name)
        print("\nCalling MCP Server...")
        result = await client.call_tool("get_weather", {"city": "Princeton"})
        print("\nAI Response:")
        print(result.content[0].text)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
