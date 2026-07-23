# Incident Assistant Gradio App — Design Spec

## Purpose

Add a Gradio web UI to `part_4_mcp_final` (the AI Incident Assistant) as an alternative to
the existing CLI (`client.py`), so the agent's investigation can be driven from a browser
and its tool-call reasoning watched live. Uses `gpt-5.4-mini` explicitly for the agent's
model.

## Scope

In scope: one new file (`part_4_mcp_final/app.py`) providing a Gradio `Blocks` UI, reusing
the existing MCP server (`server.py`) and the shared instructions/server-path constants
already defined in `client.py`. Adding `gradio` as a repo dependency. A short README update
documenting how to launch it.

Out of scope: multi-turn conversation memory (explicitly rejected — stays stateless per
question, matching `client.py`'s existing behavior), authentication, public sharing
(`share=True`), deployment/hosting concerns.

## Behavior

Each submitted question is independent (no memory across questions), consistent with
`client.py`:

1. Guard on `OPENAI_API_KEY` at startup — if missing, the UI still launches but shows a
   `gr.Markdown` warning banner instead of a broken/crashing app.
2. On submit: spin up a fresh `MCPServerStdio` (same `sys.executable` + `server.py`
   subprocess launch as `client.py`) and a fresh
   `Agent(name="Incident Assistant", instructions=INSTRUCTIONS, model="gpt-5.4-mini",
   mcp_servers=[server])` — `INSTRUCTIONS` and `SERVER_SCRIPT` are imported from `client.py`,
   not duplicated.
3. Call `Runner.run_streamed(agent, question)` and iterate `result.stream_events()`,
   live-updating a `gr.Chatbot(type="messages")`:
   - The user's question is appended immediately as a user message.
   - Each `tool_call_item` event appends an assistant message showing the tool name and
     arguments, e.g. `🔧 Calling get_order(order_id="ORD-10234")`.
   - Each `tool_call_output_item` event appends an assistant message with a truncated
     preview of the tool's output (first ~300 characters, to keep the trace readable).
   - Each `message_output_item` event appends the model's message text — the final one is
     the root-cause analysis.
   - The chatbot is updated (yielded) after every event so the trace streams live rather
     than appearing all at once at the end.
4. Any exception raised during the run is caught around the streaming loop and appended to
   the chatbot as an error message, rather than crashing the Gradio server process.
5. The question textbox and submit button are disabled while a run is in progress and
   re-enabled when it completes (success or error).

## UI layout

`gr.Blocks`, single page:

- Title (`# AI Incident Assistant`) and a one-paragraph description of the scenario
  (reused from `README.md`'s scenario section).
- `gr.Chatbot(type="messages", height=500, label="Investigation")`.
- `gr.Textbox(label="Ask about an order", placeholder="Why did order ORD-10234 fail and
  what should I do?")`, submits on Enter.
- `gr.Button("Investigate")` — same submit action as pressing Enter.
- `gr.Examples` with two ready-made questions:
  - "Why did order ORD-10234 fail and what should I do?" (payment timeout story)
  - "Why did order ORD-10190 fail and what should I do?" (inventory sync story)
- Submitting clears the chatbot before starting the new (independent) investigation.

## File responsibilities

- `part_4_mcp_final/client.py` — unchanged except that `INSTRUCTIONS` and `SERVER_SCRIPT`
  remain importable module-level constants (they already are); `app.py` imports them.
- `part_4_mcp_final/app.py` — new. Builds the Gradio `Blocks` UI, the async generator
  handler described above, and `if __name__ == "__main__": demo.launch()` (no `share=True`).
- `part_4_mcp_final/server.py`, `part_4_mcp_final/data/*.json` — unchanged.

## Dependencies

Add `gradio>=6.20.0` to root `pyproject.toml` and `requirements.txt` (same shared `uv`
environment convention as the rest of the repo).

## Testing

Manual smoke test only (consistent with the rest of this repo — no automated test
framework):

```
uv run python part_4_mcp_final/app.py
```

Open the printed local URL, submit "Why did order ORD-10234 fail and what should I do?",
confirm:
- The chatbot streams tool-call messages live (not all at once at the end).
- All four tools (`get_order`, `search_logs`, `latest_deployment`, `similar_incidents`)
  appear in the trace.
- The final message is a coherent root-cause analysis referencing the `payment-service`
  deployment and the past incident's resolution (same story validated in the original
  plan's Task 4).
- Submitting a second, unrelated question does not reference the first question's content
  (confirms statelessness).

## README

Add a short "Gradio UI" section to `part_4_mcp_final/README.md` documenting `app.py` as an
alternative to the CLI and how to launch it (`uv run python part_4_mcp_final/app.py`).
