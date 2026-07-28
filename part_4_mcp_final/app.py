import os
import sys
from pathlib import Path

import gradio as gr
from agents import Agent, ItemHelpers, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

MODEL = "gpt-5.4-mini"
SERVER_SCRIPT = str(HERE / "incident_assistant_server.py")

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

#region UI Styling
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

THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="violet")

CUSTOM_CSS = """
#header-banner {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    padding: 1.25rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}
#header-banner h1, #header-banner p, #header-banner strong {
    color: white !important;
}
#header-banner p {
    margin-top: 0.4rem !important;
    opacity: 0.92;
}
#investigate-btn {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
}
"""

#endregion

#region Helper functions
def _preview(value, limit: int = 300) -> str:
    text = str(value)
    if len(text) > limit:
        return text[:limit] + "…"
    return text
#endregion

async def investigate(question: str, history: list[dict]):
    question = (question or "").strip()
    if not question:
        yield history, "", gr.update(interactive=True), gr.update(interactive=True)
        return

    history = [{"role": "user", "content": question}]
    logs = ""
    yield history, logs, gr.update(interactive=False), gr.update(interactive=False)

    try:
        server = MCPServerStdio(
            name="incident-assistant",
            params={"command": sys.executable, "args": [SERVER_SCRIPT]},
        )
        async with server:
            agent = Agent(
                name="AI Incident Assistant",
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
                    logs += f"🔧 Calling {item.raw_item.name}({item.raw_item.arguments})\n\n"
                    yield history, logs, gr.update(interactive=False), gr.update(interactive=False)
                elif item.type == "tool_call_output_item":
                    logs += f"📋 Result: {_preview(item.output)}\n\n"
                    yield history, logs, gr.update(interactive=False), gr.update(interactive=False)
                elif item.type == "message_output_item":
                    text = ItemHelpers.text_message_output(item)
                    history.append({"role": "assistant", "content": text})
                    yield history, logs, gr.update(interactive=False), gr.update(interactive=False)
    except Exception as exc:
        history.append({"role": "assistant", "content": f"⚠️ Investigation failed: {exc}"})
        yield history, logs, gr.update(interactive=False), gr.update(interactive=False)        

    yield history, logs, gr.update(interactive=True), gr.update(interactive=True)

#region UI Components
with gr.Blocks(title="AI Incident Assistant") as demo:
    with gr.Column(elem_id="header-banner"):
        gr.Markdown("# 🛠️ AI Incident Assistant")
        gr.Markdown(SCENARIO)

    if not os.getenv("OPENAI_API_KEY"):
        gr.Markdown(
            "⚠️ **OPENAI_API_KEY is not set.** Copy `part_4_mcp_final/.env.example` to "
            "`part_4_mcp_final/.env` and set your key before investigating."
        )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=500, label="Investigation", buttons=["copy"])
        with gr.Column(scale=2):
            logs_box = gr.Textbox(
                label="🔍 Tool Trace",
                lines=21,
                max_lines=21,
                interactive=False,
                autoscroll=True,
                buttons=["copy"],
                placeholder="Tool calls and their results will appear here as the agent investigates.",
            )

    question_box = gr.Textbox(
        label="Ask about an order",
        placeholder="Why did order ORD-10234 fail and what should I do?",
    )
    submit_btn = gr.Button("🔍 Investigate", variant="primary", elem_id="investigate-btn")
    gr.Examples(examples=EXAMPLES, inputs=question_box)

    question_box.submit(
        investigate,
        inputs=[question_box, chatbot],
        outputs=[chatbot, logs_box, question_box, submit_btn],
    )
    submit_btn.click(
        investigate,
        inputs=[question_box, chatbot],
        outputs=[chatbot, logs_box, question_box, submit_btn],
    )
#endregion

if __name__ == "__main__":
    demo.launch(theme=THEME, css=CUSTOM_CSS)
