# AI Incident Assistant — Design Spec

## Purpose

Capstone sample for the `mcp-sample` teaching repo (`part_4_mcp_final`). Demonstrates an
OpenAI Agents SDK client reasoning over an MCP server with four tools to investigate a
production incident end-to-end: "Why did order ORD-10234 fail and what should I do?"

Builds on conventions established in `part_1_foundation` (LLM basics), `part_2_concepts`
(tool calling / MCP concepts), and `part_3_mcp_demo` (minimal MCP client/server/host). This
part is the first to wire a real agentic loop (OpenAI Agents SDK) to an MCP server instead
of a hand-rolled single tool call.

## Scope

In scope: one MCP server exposing four read-only tools over static JSON fixtures, one
interactive CLI client using the real `openai-agents` SDK to discover and call those tools.

Out of scope: persistence/writes, authentication, multi-server MCP composition, streaming
UI, automated tests beyond a manual smoke run.

## Folder structure

```
part_4_mcp_final/
├── server.py           # FastMCP server, 4 tools
├── client.py           # OpenAI Agents SDK client (interactive CLI)
├── data/
│   ├── orders.json
│   ├── deployments.json
│   ├── logs.json
│   └── incidents.json
├── .env.example
└── README.md
```

Flat layout, two main Python files, matching the original spec's "only two Python files"
simplicity goal.

## Server (`server.py`)

FastMCP server (`FastMCP("incident-assistant")`), following the pattern in
`part_3_mcp_demo/mcp_server.py`. Four `@server.tool()` functions. Each tool reads its JSON
file fresh from `data/` on every call (no in-memory caching) — keeps the implementation
simple and avoids stale-data surprises during a live demo.

1. **`get_order(order_id: str) -> dict`**
   Looks up the order in `orders.json` by `order_id`. Returns the full record (customer,
   status, service, amount, error, items, created_at) or a not-found message if absent.

2. **`search_logs(order_id: str) -> list[dict]`**
   Filters `logs.json` for entries matching `order_id`, sorted by `timestamp` ascending.

3. **`latest_deployment(service: str) -> dict`**
   Filters `deployments.json` for entries matching `service`, returns the one with the max
   `deployed_at`. Not-found message if the service has no deployment records.

4. **`similar_incidents(error: str) -> list[dict]`**
   Keyword-matches `error` (case-insensitive substring/word overlap) against the `error`
   field of `incidents.json` entries. Returns matching incidents with `root_cause` and
   `resolution`. Empty list if nothing matches.

All tools return plain dicts/lists (FastMCP serializes to the MCP content format
automatically). No exceptions raised for "not found" cases — a descriptive message/empty
result is returned so the agent can reason about it instead of erroring out.

## Client (`client.py`)

Uses the real `openai-agents` SDK (package `openai-agents`, import `agents`), not a
simulated loop — matches the architecture diagram's "OpenAI Agent SDK Client (Reasoning +
Tool Selection)" and the teaching goal of showing genuine agentic tool selection.

- `MCPServerStdio` launches `server.py` via `sys.executable`, same subprocess-over-stdio
  approach as `part_3_mcp_demo/mcp_client.py`.
- `Agent(name="Incident Assistant", instructions=..., mcp_servers=[server])` — instructions
  describe the role (production incident investigator) and nudge it to use the order's
  `service` field to look up deployments and its `error` field to search past incidents.
- Interactive loop: `input()` prompts for a question, `Runner.run(agent, question)` executes
  the agentic loop, prints the final root-cause analysis. Loop exits on `exit`/`quit`.
- Tools are never hardcoded into the client — the agent discovers them via MCP
  `list_tools`, same principle demonstrated in `part_3_mcp_demo`.

## Sample data

Built around the `ORD-10234` narrative so the four tools compose into one coherent story:

- **orders.json**: `ORD-10234` — status `failed`, `service: payment-service`,
  `error: PaymentGatewayTimeoutError`. Plus 2–3 other orders (some succeeded, one failed for
  an unrelated reason/service) so the agent must filter by the right `order_id`.
- **deployments.json**: a `payment-service` deployment a few minutes before the order's
  `created_at` timestamp, whose change description lowers a gateway timeout — the root
  cause. Plus older deployments for `payment-service` and 1–2 other services, so
  `latest_deployment` must pick the truly-latest one.
- **logs.json**: log lines for `ORD-10234` including the `ERROR` line with
  `PaymentGatewayTimeoutError`, plus unrelated log lines for other orders.
- **incidents.json**: a past incident (`INC-88`) with the same `error` string, whose
  `root_cause` and `resolution` explain what happened and what to do — plus 1–2 unrelated
  historical incidents.

This ensures the agent must actually call all four tools and cross-reference them (not
just echo back one record) to produce the root-cause analysis.

## Dependencies

- Add `openai-agents` to root `pyproject.toml` and `requirements.txt` (repo shares one `uv`
  environment across all `part_*` folders; no per-folder dependency files).
- Add `part_4_mcp_final/.env.example` with `OPENAI_API_KEY=sk-proj-XXXXX`, matching the
  `.env.example` convention in `part_1_foundation` / `part_2_concepts` / `part_3_mcp_demo`.

## Testing

Manual smoke test only (consistent with other `part_*` folders — no automated test suite in
this repo):

```
uv run python part_4_mcp_final/client.py
```

Ask: "Why did order ORD-10234 fail and what should I do?" Confirm the agent calls
`get_order`, `search_logs`, `latest_deployment`, and `similar_incidents` (in some order) and
produces a coherent root-cause analysis referencing the deployment and the past incident.

## README

`part_4_mcp_final/README.md` documents the scenario, architecture, folder layout, setup
(`uv sync`, set `OPENAI_API_KEY`), and how to run — following the style of the root
`README.md`.
