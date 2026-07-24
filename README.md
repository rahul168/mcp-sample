# MCP Weather Demo

A minimal example of the Model Context Protocol (MCP) with three pieces:

```
mcp-sample/
│
├── mcp_weather_demo/
│   ├── host/
│   │   └── main.py              <-- MCP Host Application
│   │
│   ├── client/
│   │   └── mcp_client.py        <-- MCP Client
│   │
│   └── server/
│       └── weather_server.py    <-- MCP Server
│
├── requirements.txt
└── README.md
```

- **mcp_weather_demo/server/weather_server.py** — an MCP server exposing a `get_weather` tool.
- **mcp_weather_demo/client/mcp_client.py** — a thin MCP client that launches the server over stdio and exposes `list_tools` / `call_tool`.
- **mcp_weather_demo/host/main.py** — the host application: wires the client to Claude, letting the model call the weather tool to answer questions.

## Setup

This project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync
export ANTHROPIC_API_KEY=your-key-here
```

## Run

```bash
uv run python -m mcp_weather_demo.host.main
```

Then ask something like `What's the weather in Tokyo?`.
