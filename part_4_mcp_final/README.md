# AI Incident Assistant

A production incident investigator built with the OpenAI Agents SDK and MCP.

## Scenario

An engineer asks: **"Why did order ORD-10234 fail and what should I do?"**

Instead of manually checking the order DB, logs, deployment history, and past
incidents, the AI assistant investigates automatically by calling MCP tools
and produces a root cause analysis.

## Architecture

```
                     User
        "Why did Order ORD-10234 fail?"
                 │
                 ▼
        OpenAI Agent SDK Client
      (Reasoning + Tool Selection)
                 │
                 │ MCP (stdio)
                 ▼
        MCP Server (FastMCP)
     ┌──────────┬──────────┬─────────────┐
     ▼          ▼          ▼             ▼
 Order DB   Log Search  Deployment DB  Incident KB
```

The agent never knows how these systems work — it discovers the four
available tools through MCP and decides which ones to call and in what order.

## Folder structure

```
part_4_mcp_final/
├── server.py           # FastMCP server exposing 4 tools
├── client.py            # OpenAI Agents SDK client (interactive CLI)
├── data/
│   ├── orders.json
│   ├── deployments.json
│   ├── logs.json
│   └── incidents.json
└── .env.example
```

## Tools

- `get_order(order_id)` — order status, service, amount, error
- `search_logs(order_id)` — log lines for that order
- `latest_deployment(service)` — most recent deployment for a service
- `similar_incidents(error)` — past incidents with the same error

## Setup

This project shares the repo-wide `uv` environment.

```bash
uv sync
cp part_4_mcp_final/.env.example part_4_mcp_final/.env
# edit part_4_mcp_final/.env and set OPENAI_API_KEY
```

## Run

```bash
uv run python part_4_mcp_final/client.py
```

Then ask: `Why did order ORD-10234 fail and what should I do?`
