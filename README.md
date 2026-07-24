# AI, LLMs, Context, Tools & MCP — Course Code

Companion code for a course that builds up from a single LLM API call to a
full AI assistant powered by the Model Context Protocol (MCP). Each part
builds on the concepts from the last:

```
mcp-sample/
│
├── part_1_foundation/   <-- Section 1: talking to an LLM for the first time
├── part_2_concepts/     <-- Section 2: context, structured output, tool calling, MCP
├── part_3_mcp_demo/     <-- Section 3: a hand-built MCP server, client & host
├── part_4_mcp_final/    <-- Section 4: a full AI Incident Assistant (agent + MCP + Gradio UI)
│
├── pyproject.toml
└── requirements.txt
```

## Part 1 — Foundation

`part_1_foundation/` — the simplest possible programs that talk to an LLM,
building up from a raw API call to a reusable request/response helper:

- **main_v0.py** — a single call via the OpenAI Responses API.
- **main_v1.py** — the same call via Chat Completions, with a request/response helper.
- **main_v2.py** — the same call routed through [LiteLLM](https://docs.litellm.ai/) instead of a provider-specific SDK.

## Part 2 — Concepts

`part_2_concepts/` — Jupyter notebooks covering the ideas that turn a bare
LLM into something that can act:

- **nb_1_litellm_benefits.ipynb** — why use LiteLLM instead of wiring up each provider's SDK.
- **nb_2_llm_context.ipynb** — building up the idea of context, from a stateless call to production techniques.
- **nb_3_structured_output.ipynb** — going from free-text responses to typed, structured output.
- **nb_4_tool_calling.ipynb** — tool/function calling, from plain chat to agents.
- **nb_5_mcp_calling.ipynb** — the Model Context Protocol, from a plain SDK call to a full LLM + MCP round trip.

## Part 3 — Build an MCP Server

`part_3_mcp_demo/` — a minimal, hand-built MCP server, client, and host application:

- **mcp_server.py** — an MCP server (FastMCP) exposing a `get_weather` tool.
- **mcp_client.py** — a thin MCP client that launches the server over stdio and exposes `list_tools` / `call_tool`.
- **mcp_host.py** — the host application that connects the client and calls the tool.

Run it with:

```bash
uv run python part_3_mcp_demo/mcp_host.py
```

## Part 4 — AI Incident Assistant

`part_4_mcp_final/` — everything from parts 1-3 assembled into a real
application: an agent (OpenAI Agents SDK) that investigates failed orders by
calling tools exposed over MCP, with a Gradio web UI. See
[part_4_mcp_final/README.md](part_4_mcp_final/README.md) for details on
running it.

## Getting Started

Clone the repo to your machine:

```bash
git clone https://github.com/rahul168/mcp-sample.git
cd mcp-sample
```

Then follow the [Setup](#setup) steps below before running any part of the course.

## Setup

This project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Each part that needs API keys ships a `.env.example` — copy it to `.env` in
that part's folder and fill in the values (e.g. `OPENAI_API_KEY`).

```bash
cp part_1_foundation/.env.example part_1_foundation/.env
```
