# AI Incident Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `part_4_mcp_final`, a two-file MCP demo (FastMCP server + OpenAI Agents SDK client) where an agent investigates why order `ORD-10234` failed by calling four tools: `get_order`, `search_logs`, `latest_deployment`, `similar_incidents`.

**Architecture:** A FastMCP server (`server.py`) exposes four read-only tools backed by static JSON fixtures in `data/`. An interactive CLI client (`client.py`) launches that server over stdio via the real `openai-agents` SDK (`MCPServerStdio` + `Agent` + `Runner`), letting the model discover and call the tools itself — no tool logic is hardcoded into the client.

**Tech Stack:** Python 3.12, `mcp` (FastMCP), `openai-agents`, `python-dotenv`, `uv` (shared repo-wide environment).

## Global Constraints

- Python `>=3.12` (matches root `pyproject.toml` `requires-python`).
- Single shared `uv` environment for the whole repo — no per-folder `requirements.txt`; add new deps to root `pyproject.toml` and `requirements.txt`.
- Flat folder layout under `part_4_mcp_final/`: `server.py`, `client.py`, `data/*.json`, `.env.example`, `README.md` — no subpackages.
- Follow `part_3_mcp_demo` conventions: `FastMCP("<name>")` server, stdio transport, `sys.executable` to launch the server subprocess.
- `.env` files are already gitignored repo-wide; only commit `.env.example`.
- No automated test framework in this repo (no `pytest` dependency) — verification steps use ad-hoc `uv run python` commands, matching the rest of the repo.

---

### Task 1: Sample data fixtures

**Files:**
- Create: `part_4_mcp_final/data/orders.json`
- Create: `part_4_mcp_final/data/deployments.json`
- Create: `part_4_mcp_final/data/logs.json`
- Create: `part_4_mcp_final/data/incidents.json`

**Interfaces:**
- Produces: the four JSON fixtures that Task 2's tools read. Schemas below are exact and must match field names used in Task 2.
  - Order record: `order_id, customer, status, service, amount, items, created_at, error` (error is `null` when status is not failed)
  - Deployment record: `service, version, deployed_at, deployed_by, change`
  - Log record: `order_id, timestamp, level, service, message`
  - Incident record: `incident_id, error, date, root_cause, resolution`

- [ ] **Step 1: Create `part_4_mcp_final/data/orders.json`**

```json
[
  {
    "order_id": "ORD-10234",
    "customer": "Alice Johnson",
    "status": "failed",
    "service": "payment-service",
    "amount": 129.99,
    "items": ["Wireless Mouse", "USB-C Hub"],
    "created_at": "2026-07-22T14:32:10Z",
    "error": "PaymentGatewayTimeoutError"
  },
  {
    "order_id": "ORD-10235",
    "customer": "Marcus Lee",
    "status": "completed",
    "service": "payment-service",
    "amount": 49.50,
    "items": ["Phone Case"],
    "created_at": "2026-07-22T15:01:44Z",
    "error": null
  },
  {
    "order_id": "ORD-10190",
    "customer": "Priya Nair",
    "status": "failed",
    "service": "inventory-service",
    "amount": 89.00,
    "items": ["Mechanical Keyboard"],
    "created_at": "2026-07-21T09:12:03Z",
    "error": "InventorySyncError"
  },
  {
    "order_id": "ORD-10201",
    "customer": "Diego Fernandez",
    "status": "completed",
    "service": "order-service",
    "amount": 15.25,
    "items": ["USB Cable"],
    "created_at": "2026-07-21T11:45:30Z",
    "error": null
  }
]
```

- [ ] **Step 2: Create `part_4_mcp_final/data/deployments.json`**

```json
[
  {
    "service": "payment-service",
    "version": "v2.14.0",
    "deployed_at": "2026-07-22T14:15:00Z",
    "deployed_by": "ci-bot",
    "change": "Upgraded payment gateway SDK from 3.2.1 to 4.0.0; new SDK default request timeout dropped from 60s to 30s"
  },
  {
    "service": "payment-service",
    "version": "v2.13.2",
    "deployed_at": "2026-07-18T09:00:00Z",
    "deployed_by": "ci-bot",
    "change": "Fixed currency rounding bug in refund calculation"
  },
  {
    "service": "inventory-service",
    "version": "v1.8.0",
    "deployed_at": "2026-07-20T16:30:00Z",
    "deployed_by": "ci-bot",
    "change": "Migrated inventory sync job to new message queue"
  },
  {
    "service": "order-service",
    "version": "v3.1.0",
    "deployed_at": "2026-07-19T10:00:00Z",
    "deployed_by": "ci-bot",
    "change": "Added support for split shipments"
  }
]
```

- [ ] **Step 3: Create `part_4_mcp_final/data/logs.json`**

```json
[
  {
    "order_id": "ORD-10234",
    "timestamp": "2026-07-22T14:32:09Z",
    "level": "INFO",
    "service": "order-service",
    "message": "Order ORD-10234 created, forwarding to payment-service"
  },
  {
    "order_id": "ORD-10234",
    "timestamp": "2026-07-22T14:32:10Z",
    "level": "INFO",
    "service": "payment-service",
    "message": "Charging $129.99 to card ending 4242"
  },
  {
    "order_id": "ORD-10234",
    "timestamp": "2026-07-22T14:32:40Z",
    "level": "ERROR",
    "service": "payment-service",
    "message": "PaymentGatewayTimeoutError: request to payment gateway timed out after 30s"
  },
  {
    "order_id": "ORD-10234",
    "timestamp": "2026-07-22T14:32:41Z",
    "level": "ERROR",
    "service": "order-service",
    "message": "Order ORD-10234 marked as failed: downstream payment-service error"
  },
  {
    "order_id": "ORD-10235",
    "timestamp": "2026-07-22T15:01:44Z",
    "level": "INFO",
    "service": "payment-service",
    "message": "Charging $49.50 to card ending 1187"
  },
  {
    "order_id": "ORD-10235",
    "timestamp": "2026-07-22T15:01:45Z",
    "level": "INFO",
    "service": "payment-service",
    "message": "Payment succeeded for order ORD-10235"
  },
  {
    "order_id": "ORD-10190",
    "timestamp": "2026-07-21T09:12:05Z",
    "level": "ERROR",
    "service": "inventory-service",
    "message": "InventorySyncError: stock record not found for SKU MK-2201"
  },
  {
    "order_id": "ORD-10201",
    "timestamp": "2026-07-21T11:45:31Z",
    "level": "INFO",
    "service": "order-service",
    "message": "Order ORD-10201 completed successfully"
  }
]
```

- [ ] **Step 4: Create `part_4_mcp_final/data/incidents.json`**

```json
[
  {
    "incident_id": "INC-88",
    "error": "PaymentGatewayTimeoutError",
    "date": "2026-05-03",
    "root_cause": "A payment gateway SDK upgrade lowered the default request timeout from 60s to 30s, which was too aggressive during peak traffic and caused legitimate slow-but-successful gateway calls to be aborted.",
    "resolution": "Rolled back the SDK to the previous version and, when re-upgrading, explicitly set the client timeout to 60s instead of relying on the SDK default."
  },
  {
    "incident_id": "INC-45",
    "error": "InventorySyncError",
    "date": "2026-04-11",
    "root_cause": "A stock migration script skipped SKUs added after the migration started, leaving their inventory records missing.",
    "resolution": "Re-ran the migration script in reconciliation mode to backfill missing SKU records."
  },
  {
    "incident_id": "INC-12",
    "error": "OrderValidationError",
    "date": "2026-03-02",
    "root_cause": "A new shipping address format was not accepted by the legacy validation regex.",
    "resolution": "Updated the validation regex to support the new address format."
  }
]
```

- [ ] **Step 5: Verify all four files are valid JSON**

Run:
```bash
uv run python -c "
import json
for f in ['orders', 'deployments', 'logs', 'incidents']:
    data = json.load(open(f'part_4_mcp_final/data/{f}.json'))
    print(f, len(data), 'records')
"
```
Expected:
```
orders 4 records
deployments 4 records
logs 8 records
incidents 3 records
```

- [ ] **Step 6: Commit**

```bash
git add part_4_mcp_final/data/
git commit -m "Add sample data fixtures for incident assistant"
```

---

### Task 2: MCP server with four tools

**Files:**
- Create: `part_4_mcp_final/server.py`

**Interfaces:**
- Consumes: JSON fixtures from Task 1 (`part_4_mcp_final/data/orders.json`, `deployments.json`, `logs.json`, `incidents.json`), read relative to `Path(__file__).parent / "data"`.
- Produces: an MCP stdio server named `"incident-assistant"` exposing exactly four tools that Task 4's client will connect to:
  - `get_order(order_id: str) -> dict`
  - `search_logs(order_id: str) -> list[dict]`
  - `latest_deployment(service: str) -> dict`
  - `similar_incidents(error: str) -> list[dict]`

- [ ] **Step 1: Write `part_4_mcp_final/server.py`**

```python
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

server = FastMCP("incident-assistant")

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load(filename: str):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


@server.tool()
def get_order(order_id: str) -> dict:
    """
    Look up an order by its ID. Returns customer, status, service, amount,
    items, created_at, and error (if the order failed).
    """
    for order in _load("orders.json"):
        if order["order_id"] == order_id:
            return order
    return {"error": f"No order found with id '{order_id}'"}


@server.tool()
def search_logs(order_id: str) -> list[dict]:
    """
    Return all log lines associated with an order ID, sorted by timestamp.
    """
    matches = [log for log in _load("logs.json") if log["order_id"] == order_id]
    matches.sort(key=lambda log: log["timestamp"])
    return matches


@server.tool()
def latest_deployment(service: str) -> dict:
    """
    Return the most recent deployment record for a given service name.
    """
    matches = [d for d in _load("deployments.json") if d["service"] == service]
    if not matches:
        return {"error": f"No deployment records found for service '{service}'"}
    return max(matches, key=lambda d: d["deployed_at"])


@server.tool()
def similar_incidents(error: str) -> list[dict]:
    """
    Search past incidents for ones whose error matches the given error
    string. Returns each match's root cause and resolution.
    """
    needle = error.lower()
    return [
        incident
        for incident in _load("incidents.json")
        if needle in incident["error"].lower() or incident["error"].lower() in needle
    ]


if __name__ == "__main__":
    print("Incident Assistant MCP server running...")
    server.run()
```

- [ ] **Step 2: Verify tool discovery and each tool's output**

Run (from the repo root):
```bash
cd part_4_mcp_final && uv run python - <<'PY'
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", sorted(t.name for t in tools.tools))

            r = await session.call_tool("get_order", {"order_id": "ORD-10234"})
            print("ORDER:", r.content[0].text)

            r = await session.call_tool("search_logs", {"order_id": "ORD-10234"})
            print("LOGS COUNT:", r.content[0].text.count('"order_id"'))

            r = await session.call_tool("latest_deployment", {"service": "payment-service"})
            print("DEPLOYMENT:", r.content[0].text)

            r = await session.call_tool("similar_incidents", {"error": "PaymentGatewayTimeoutError"})
            print("INCIDENTS:", r.content[0].text)

asyncio.run(main())
PY
cd ..
```
Expected output (order of keys within JSON may vary, content must match):
```
TOOLS: ['get_order', 'latest_deployment', 'search_logs', 'similar_incidents']
ORDER: ..."order_id": "ORD-10234"..."error": "PaymentGatewayTimeoutError"...
LOGS COUNT: 4
DEPLOYMENT: ...v2.14.0...
INCIDENTS: ...INC-88...
```

- [ ] **Step 3: Commit**

```bash
git add part_4_mcp_final/server.py
git commit -m "Add incident-assistant MCP server with four tools"
```

---

### Task 3: Add `openai-agents` dependency and `.env.example`

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`
- Create: `part_4_mcp_final/.env.example`

**Interfaces:**
- Produces: an importable `agents` package (from PyPI `openai-agents`) available in the shared `uv` environment, which Task 4's `client.py` imports as `from agents import Agent, Runner` and `from agents.mcp import MCPServerStdio`.

- [ ] **Step 1: Add `openai-agents` to `pyproject.toml`**

In `pyproject.toml`, add `"openai-agents>=0.18.0",` to the `dependencies` list (alphabetically, after `"nbconvert>=7.16.0",` and before `"openai>=1.68.0",`):

```toml
dependencies = [
    "anthropic>=0.40.0",
    "ipykernel>=6.29.0",
    "langchain>=1.3.0",
    "langchain-core>=1.5.0",
    "langchain-openai>=1.4.0",
    "litellm>=1.80.0",
    "mcp>=1.0.0",
    "nbconvert>=7.16.0",
    "openai>=1.68.0",
    "openai-agents>=0.18.0",
    "python-dotenv>=1.0.0",
    "tiktoken>=0.13.0",
]
```

- [ ] **Step 2: Add `openai-agents` to `requirements.txt`**

Add `openai-agents>=0.18.0` as a new line in `requirements.txt`:

```
mcp>=1.0.0
anthropic>=0.40.0
openai>=1.68.0
openai-agents>=0.18.0
python-dotenv>=1.0.0
litellm>=1.80.0
langchain-core>=1.5.0
langchain-openai>=1.4.0
ipykernel>=6.29.0
nbconvert>=7.16.0
tiktoken>=0.13.0
```

- [ ] **Step 3: Sync the environment and verify the import**

Run:
```bash
uv sync
uv run python -c "from agents import Agent, Runner; from agents.mcp import MCPServerStdio; print('agents SDK ok')"
```
Expected: `agents SDK ok` printed with no errors, and `uv.lock` updated (shows as modified in `git status`).

- [ ] **Step 4: Create `part_4_mcp_final/.env.example`**

```
OPENAI_API_KEY=sk-proj-XXXXX
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt uv.lock part_4_mcp_final/.env.example
git commit -m "Add openai-agents dependency for incident assistant client"
```

---

### Task 4: Interactive agent client

**Files:**
- Create: `part_4_mcp_final/client.py`

**Interfaces:**
- Consumes: `agents.Agent`, `agents.Runner`, `agents.mcp.MCPServerStdio` (Task 3); launches `part_4_mcp_final/server.py` (Task 2) as a subprocess over stdio.
- Produces: a runnable CLI entry point (`python client.py`) — no other task depends on this module's internals.

- [ ] **Step 1: Write `part_4_mcp_final/client.py`**

```python
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
4. Call similar_incidents with the order's error to check whether this
   has happened before, and how it was resolved.

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
```

- [ ] **Step 2: Set up the API key**

```bash
cp part_4_mcp_final/.env.example part_4_mcp_final/.env
```
Edit `part_4_mcp_final/.env` and set a real `OPENAI_API_KEY` (same key already used by `part_1_foundation`/`part_2_concepts`/`part_3_mcp_demo` if available).

- [ ] **Step 3: Manual acceptance test (requires a live OPENAI_API_KEY)**

Run:
```bash
uv run python part_4_mcp_final/client.py
```
At the `>` prompt, type:
```
Why did order ORD-10234 fail and what should I do?
```
Expected: the agent's response references the `PaymentGatewayTimeoutError`, ties it to the `payment-service` deployment that dropped the timeout from 60s to 30s, and recommends the fix from incident `INC-88` (roll back / set an explicit 60s timeout). Type `exit` to quit.

- [ ] **Step 4: Commit**

```bash
git add part_4_mcp_final/client.py
git commit -m "Add interactive OpenAI Agents SDK client for incident assistant"
```

---

### Task 5: README

**Files:**
- Create: `part_4_mcp_final/README.md`

**Interfaces:**
- Consumes: nothing (documentation only).

- [ ] **Step 1: Write `part_4_mcp_final/README.md`**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add part_4_mcp_final/README.md
git commit -m "Add README for incident assistant"
```

---

## Self-Review Notes

- **Spec coverage:** all four tools (Task 2), sample data telling one coherent story (Task 1), real `openai-agents` SDK client with tool auto-discovery (Task 4), `.env.example` + dependency wiring (Task 3), README (Task 5), manual smoke test (Task 4 Step 3) — all spec sections covered.
- **Type consistency:** `get_order`/`search_logs`/`latest_deployment`/`similar_incidents` signatures and field names (`order_id`, `service`, `error`, `deployed_at`, etc.) are identical between Task 1's fixtures, Task 2's server, and Task 4's client instructions.
- **No placeholders:** every step has complete file contents or a runnable command with expected output.
