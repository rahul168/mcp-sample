# Incident Assistant Gradio App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Gradio web UI (`part_4_mcp_final/app.py`) that drives the existing AI Incident
Assistant agent, streaming tool calls live to a chat window, using `gpt-5.4-mini` explicitly.

**Architecture:** One new file, `app.py`, that imports `INSTRUCTIONS` and `SERVER_SCRIPT` from
the existing `client.py`, builds a `gr.Blocks` UI, and on each submitted question spins up a
fresh `MCPServerStdio` + `Agent`, calling `Runner.run_streamed(...)` and forwarding
`stream_events()` into a `gr.Chatbot`. Each question is independent — no memory carried
between questions, matching `client.py`'s existing per-call behavior.

**Tech Stack:** Python 3.12, `gradio>=6.20.0`, `openai-agents` (already a dependency),
`mcp` (already a dependency), shared repo-wide `uv` environment.

## Global Constraints

- Python `>=3.12`, single shared `uv` environment for the whole repo (`pyproject.toml` +
  `requirements.txt` kept in sync, `uv sync` regenerates `uv.lock`).
- `gradio>=6.20.0` (confirmed via `uv pip install --dry-run gradio` → resolves to
  `gradio==6.20.0`) — added to both `pyproject.toml`'s `dependencies` list (alphabetical
  order) and `requirements.txt`.
- No new file duplicates `INSTRUCTIONS` or `SERVER_SCRIPT` — `app.py` imports both from
  `part_4_mcp_final/client.py`.
- Model is set explicitly to `"gpt-5.4-mini"` on the `Agent` in `app.py` (this is currently
  the SDK default when unspecified, per context7 docs for
  `/openai/openai-agents-python`, but the spec requires it stated explicitly).
- Stateless: every submitted question starts a brand new `MCPServerStdio` + `Agent` +
  `Runner.run_streamed` — no session/thread memory across questions.
- No automated test framework in this repo — verification is manual `uv run python ...`
  smoke testing, consistent with `part_1`–`part_4`.
- `.env` handling and `OPENAI_API_KEY` guard follow `client.py`'s existing pattern
  (`HERE = Path(__file__).resolve().parent`, `load_dotenv(HERE / ".env")`) but must not
  crash the process if the key is missing — show a banner in the UI instead (this differs
  from `client.py`, which exits via `sys.exit(1)`).
- No `share=True` on `demo.launch()`.

---

### Task 1: Add `gradio` dependency

**Files:**
- Modify: `pyproject.toml:6-19` (dependencies list)
- Modify: `requirements.txt`

**Interfaces:**
- Produces: `gradio` importable as `import gradio as gr` for Task 2.

- [ ] **Step 1: Add `gradio` to `pyproject.toml`'s dependencies list, alphabetically**

Current `dependencies` list in `pyproject.toml`:

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
    "openai-agents>=0.18.0",
    "openai>=1.68.0",
    "python-dotenv>=1.0.0",
    "tiktoken>=0.13.0",
]
```

Change it to (adds `"gradio>=6.20.0",` alphabetically between `"anthropic>=0.40.0",` and
`"ipykernel>=6.29.0",`):

```toml
dependencies = [
    "anthropic>=0.40.0",
    "gradio>=6.20.0",
    "ipykernel>=6.29.0",
    "langchain>=1.3.0",
    "langchain-core>=1.5.0",
    "langchain-openai>=1.4.0",
    "litellm>=1.80.0",
    "mcp>=1.0.0",
    "nbconvert>=7.16.0",
    "openai-agents>=0.18.0",
    "openai>=1.68.0",
    "python-dotenv>=1.0.0",
    "tiktoken>=0.13.0",
]
```

- [ ] **Step 2: Add `gradio` to `requirements.txt`**

Current `requirements.txt`:

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

Add a `gradio>=6.20.0` line at the end:

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
gradio>=6.20.0
```

- [ ] **Step 3: Sync the environment**

Run: `uv sync`
Expected: Output includes a line installing `gradio` (version `6.20.0` or newer) and
completes without error.

- [ ] **Step 4: Verify gradio imports**

Run: `uv run python -c "import gradio as gr; print(gr.__version__)"`
Expected: Prints a version string (e.g. `6.20.0`) with no errors.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt uv.lock
git commit -m "Add gradio dependency for incident-assistant web UI"
```

---

### Task 2: Create `app.py` with the Gradio UI

**Files:**
- Create: `part_4_mcp_final/app.py`

**Interfaces:**
- Consumes from `part_4_mcp_final/client.py`: module-level constants `INSTRUCTIONS: str` and
  `SERVER_SCRIPT: str` (both already defined and exported at module scope in `client.py`).
- Consumes from `agents`: `Agent`, `Runner`, `ItemHelpers`.
- Consumes from `agents.mcp`: `MCPServerStdio`.
- Produces: `part_4_mcp_final/app.py`, runnable standalone via
  `uv run python part_4_mcp_final/app.py`, launching a local Gradio server.

- [ ] **Step 1: Write `part_4_mcp_final/app.py`**

```python
import os
import sys

import gradio as gr
from agents import Agent, ItemHelpers, Runner
from agents.mcp import MCPServerStdio

from client import INSTRUCTIONS, SERVER_SCRIPT

MODEL = "gpt-5.4-mini"

SCENARIO = (
    "An engineer asks: **\"Why did order ORD-10234 fail and what should I do?\"** "
    "Instead of manually checking the order DB, logs, deployment history, and past "
    "incidents, this assistant investigates automatically by calling MCP tools and "
    "produces a root cause analysis."
)

EXAMPLES = [
    "Why did order ORD-10234 fail and what should I do?",
    "Why did order ORD-10190 fail and what should I do?",
]


def _preview(value, limit: int = 300) -> str:
    text = str(value)
    if len(text) > limit:
        return text[:limit] + "…"
    return text


async def investigate(question: str, history: list[dict]):
    question = (question or "").strip()
    if not question:
        yield history, gr.update(interactive=True), gr.update(interactive=True)
        return

    history = [{"role": "user", "content": question}]
    yield history, gr.update(interactive=False), gr.update(interactive=False)

    try:
        async with MCPServerStdio(
            name="incident-assistant",
            params={"command": sys.executable, "args": [SERVER_SCRIPT]},
        ) as server:
            agent = Agent(
                name="Incident Assistant",
                instructions=INSTRUCTIONS,
                model=MODEL,
                mcp_servers=[server],
            )

            result = Runner.run_streamed(agent, question)
            async for event in result.stream_events():
                if event.type != "run_item_stream_event":
                    continue

                item = event.item
                if item.type == "tool_call_item":
                    name = item.raw_item.name
                    args = item.raw_item.arguments
                    history.append(
                        {"role": "assistant", "content": f"🔧 Calling {name}({args})"}
                    )
                    yield history, gr.update(interactive=False), gr.update(interactive=False)
                elif item.type == "tool_call_output_item":
                    history.append(
                        {"role": "assistant", "content": f"📋 {_preview(item.output)}"}
                    )
                    yield history, gr.update(interactive=False), gr.update(interactive=False)
                elif item.type == "message_output_item":
                    text = ItemHelpers.text_message_output(item)
                    history.append({"role": "assistant", "content": text})
                    yield history, gr.update(interactive=False), gr.update(interactive=False)
    except Exception as exc:
        history.append({"role": "assistant", "content": f"⚠️ Investigation failed: {exc}"})
        yield history, gr.update(interactive=True), gr.update(interactive=True)
        return

    yield history, gr.update(interactive=True), gr.update(interactive=True)


with gr.Blocks(title="AI Incident Assistant") as demo:
    gr.Markdown("# AI Incident Assistant")
    gr.Markdown(SCENARIO)

    if not os.getenv("OPENAI_API_KEY"):
        gr.Markdown(
            "⚠️ **OPENAI_API_KEY is not set.** Copy `part_4_mcp_final/.env.example` to "
            "`part_4_mcp_final/.env` and set your key before investigating."
        )

    chatbot = gr.Chatbot(type="messages", height=500, label="Investigation")
    question_box = gr.Textbox(
        label="Ask about an order",
        placeholder="Why did order ORD-10234 fail and what should I do?",
    )
    submit_btn = gr.Button("Investigate")
    gr.Examples(examples=EXAMPLES, inputs=question_box)

    question_box.submit(
        investigate, inputs=[question_box, chatbot], outputs=[chatbot, question_box, submit_btn]
    )
    submit_btn.click(
        investigate, inputs=[question_box, chatbot], outputs=[chatbot, question_box, submit_btn]
    )


if __name__ == "__main__":
    demo.launch()
```

- [ ] **Step 2: Verify the module imports and builds without a running server**

Run (from `part_4_mcp_final/`):
`uv run python -c "import app; print(type(app.demo))"`
Expected: Prints `<class 'gradio.blocks.Blocks'>` with no errors or tracebacks.

- [ ] **Step 3: Manually launch and smoke-test the app**

Run (from `part_4_mcp_final/`): `uv run python app.py`
Expected: Terminal prints a local URL (e.g. `http://127.0.0.1:7860`). Open it in a browser
and confirm:
- The page shows the title, scenario blurb, and (if `OPENAI_API_KEY` is unset) the warning
  banner.
- Click the first example, then "Investigate". The chatbot streams messages live: the user
  question, four `🔧 Calling ...` tool-call messages (one per tool:
  `get_order`, `search_logs`, `latest_deployment`, `similar_incidents`, in some order), their
  `📋 ...` output previews, and a final root-cause-analysis message referencing the
  `payment-service` deployment and the `INC-88` resolution.
- The textbox and button are disabled while the run is in progress and re-enabled after.
- Submit the second example (`ORD-10190`). Confirm the chatbot clears and shows only the new
  investigation (no leftover content from the first question), confirming statelessness.
- Stop the server with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add part_4_mcp_final/app.py
git commit -m "Add Gradio UI for incident-assistant agent"
```

---

### Task 3: Document the Gradio UI in the README

**Files:**
- Modify: `part_4_mcp_final/README.md`

**Interfaces:**
- None (documentation only).

- [ ] **Step 1: Add `app.py` to the folder structure diagram**

Current folder structure block in `part_4_mcp_final/README.md`:

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

Replace with:

```
part_4_mcp_final/
├── server.py           # FastMCP server exposing 4 tools
├── client.py            # OpenAI Agents SDK client (interactive CLI)
├── app.py               # Gradio web UI (streams tool calls live)
├── data/
│   ├── orders.json
│   ├── deployments.json
│   ├── logs.json
│   └── incidents.json
└── .env.example
```

- [ ] **Step 2: Add a "Gradio UI" section after the existing "Run" section**

Current end of file:

```
## Run

```bash
uv run python part_4_mcp_final/client.py
```

Then ask: `Why did order ORD-10234 fail and what should I do?`
```

Append a new section after it:

```
## Gradio UI

As an alternative to the CLI, a browser-based UI is available that streams each tool call
live as the agent investigates:

```bash
uv run python part_4_mcp_final/app.py
```

Open the printed local URL, then ask a question (or click one of the provided examples).
Each investigation is independent — no conversation memory is kept between questions.
```

- [ ] **Step 3: Commit**

```bash
git add part_4_mcp_final/README.md
git commit -m "Document Gradio UI in part_4_mcp_final README"
```
