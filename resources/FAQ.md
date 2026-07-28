# FAQ – Helpful Resources for Getting Started

This FAQ document provides helpful resources and explanations for tools and concepts commonly used in this course.

---

# Table of Contents

1. What should I install before starting this course?
2. What is Cursor and how is it different from VS Code?
3. What is uv and why does this course use it?
4. How do I set up and run this project?
5. How do I run the Jupyter notebooks (`.ipynb`) in Cursor?
6. What is Git and why should I learn it?
7. How to install Git?
8. What is GitHub?
9. What is the Model Context Protocol (MCP)?
10. What is LiteLLM?
11. What are AI agents and the OpenAI Agents SDK?
12. What is Gradio?
13. Where can I learn more about LLMs, agents, and MCP?
14. How to contact if I am completely stuck?

---

# 1. What should I install before starting this course?

For this course, you should install:

* **Cursor** — the AI code editor used throughout the course
* **uv** — the Python package/environment manager this project uses (it fetches the right Python version for you, so you don't need to install Python separately)
* **Node.js** (LTS, 18+) — needed to run MCP servers distributed as npm packages, and some Cursor/VS Code tooling
* **Git**

Helpful links:

* Cursor: [https://cursor.com/downloads](https://cursor.com/downloads)
* uv: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
* Node.js: [https://nodejs.org/](https://nodejs.org/)
* Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)

Recommended Cursor extensions:

* Python
* Jupyter (`ms-toolsai.jupyter`)

See the main [README.md](../README.md) for the full Prerequisites section.

---

# 2. What is Cursor and how is it different from VS Code?

Cursor is an AI-native code editor built on top of VS Code. It supports the
same extensions (including Python and Jupyter), keybindings, and settings as
VS Code, but adds AI features like chat, inline code generation, and agentic
edits directly in the editor.

Because Cursor is VS Code under the hood, anything you already know about
VS Code (extensions, debugging, terminals, notebooks) carries over directly.

Helpful resources:

* Cursor Docs: [https://docs.cursor.com/](https://docs.cursor.com/)

---

# 3. What is uv and why does this course use it?

uv is a fast Python package and environment manager. It can replace tools
like:

* pip
* virtualenv
* pyenv (partially)

Benefits:

* Very fast package installation
* Automatically installs and manages the right Python version for the project (see `.python-version`)
* One command (`uv sync`) sets up a working virtual environment for the whole repo

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Common commands used in this course:

```bash
uv sync              # create/update the .venv with all dependencies
uv run python <file> # run a script inside the project's virtual environment
```

Helpful resources:

* uv Documentation: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

---

# 4. How do I set up and run this project?

Clone the repo, then install dependencies with uv:

```bash
git clone https://github.com/rahul168/mcp-sample.git
cd mcp-sample
uv sync
```

Each part that needs API keys ships a `.env.example` file — copy it to
`.env` in that part's folder and fill in the values (e.g.
`OPENAI_API_KEY`):

```bash
cp part_1_foundation/.env.example part_1_foundation/.env
```

Then run any script with `uv run`, for example:

```bash
uv run python part_3_mcp_demo/mcp_host.py
```

See the main [README.md](../README.md) for a walkthrough of what each part
(`part_1_foundation` → `part_4_mcp_final`) covers.

---

# 5. How do I run the Jupyter notebooks (`.ipynb`) in Cursor?

Part 2 of the course (`part_2_concepts/`) uses Jupyter notebooks. Since
Cursor is VS Code-based, it uses the same Jupyter extension:

1. Install the **Jupyter** extension (`ms-toolsai.jupyter`) from the Extensions panel in Cursor.
2. Run `uv sync` first so the `.venv` and `ipykernel` exist.
3. Open any `.ipynb` file in `part_2_concepts/`, click **Select Kernel** (top-right of the notebook), and choose the interpreter at `.venv/bin/python` in this repo.
4. Run a cell — Cursor will prompt to install any missing kernel dependencies if needed.

Helpful resources:

* JupyterLab Docs: [https://jupyterlab.readthedocs.io/](https://jupyterlab.readthedocs.io/)
* Project Jupyter: [https://jupyter.org/](https://jupyter.org/)

---

# 6. What is Git and why should I learn it?

Git is a version control system that helps you:

* Track changes in your code
* Restore previous versions
* Collaborate with others
* Save your projects safely

Basic Git commands:

```bash
git init
git status
git add .
git commit -m "Initial commit"
git push
```

Beginner resources:

* Git Documentation: [https://git-scm.com/doc](https://git-scm.com/doc)
* GitHub Skills: [https://skills.github.com/](https://skills.github.com/)

---

# 7. How to install Git?

Go to git-scm.com and download the version suitable for your OS. Once
installed, open a terminal and configure Git with your username and email
using these commands:

```bash
git config --global user.name "Your Name"
git config --global user.email "youremail@example.com"
```

This tells Git who is making the changes in your projects.

---

# 8. What is GitHub?

GitHub is a cloud platform where you can host your Git repositories.

Steps to push your project to GitHub:

1. Create a repository on GitHub.
2. Connect your local repo to GitHub.
3. Run the following commands to push your code online:

```bash
git remote add origin https://github.com/yourusername/repo.git
git branch -M main
git push -u origin main
```

---

# 9. What is the Model Context Protocol (MCP)?

MCP is an open protocol that standardizes how AI applications connect LLMs
to external tools, data sources, and systems. Instead of writing
provider-specific or one-off integrations for every tool, you expose tools
through an MCP **server**, and any MCP-compatible **client**/**host**
(including this course's `mcp_host.py`) can discover and call them.

This course builds MCP up in layers:

* `part_2_concepts/nb_5_mcp_calling.ipynb` — going from a plain SDK call to a full LLM + MCP round trip.
* `part_3_mcp_demo/` — a minimal, hand-built MCP server, client, and host.
* `part_4_mcp_final/` — a real application (AI Incident Assistant) where an agent calls MCP tools to investigate failed orders.

Helpful resources:

* MCP Documentation: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
* MCP Specification: [https://spec.modelcontextprotocol.io/](https://spec.modelcontextprotocol.io/)
* FastMCP (the Python framework used to build the server in this course): [https://gofastmcp.com/](https://gofastmcp.com/)

---

# 10. What is LiteLLM?

LiteLLM is a library that gives you one consistent interface for calling
many different LLM providers (OpenAI, Anthropic, Google, and more) instead
of learning each provider's SDK separately.

`part_1_foundation/main_v2.py` shows the same request routed through
LiteLLM instead of a provider-specific SDK, and
`part_2_concepts/nb_1_litellm_benefits.ipynb` walks through why that's
useful.

Helpful resources:

* LiteLLM Docs: [https://docs.litellm.ai/](https://docs.litellm.ai/)

---

# 11. What are AI agents and the OpenAI Agents SDK?

An "agent" is an LLM that can reason about a task, decide which tools to
call (and in what order), and use the results to keep working toward a
goal — instead of just returning a single text reply.

`part_4_mcp_final/` uses the OpenAI Agents SDK to build an agent that
investigates failed orders by calling MCP tools (order lookup, log search,
deployment history, past incidents) and produces a root-cause analysis.
`part_2_concepts/nb_4_tool_calling.ipynb` builds up to this idea, starting
from plain tool/function calling.

Helpful resources:

* OpenAI Agents SDK Docs: [https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/)
* OpenAI Function Calling Guide: [https://platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)

---

# 12. What is Gradio?

Gradio is a Python library for quickly building web UIs for machine
learning and AI applications, without writing frontend code.

`part_4_mcp_final/app.py` uses Gradio to give the AI Incident Assistant a
simple chat-style web UI that streams tool calls live as the agent
investigates.

Helpful resources:

* Gradio Docs: [https://www.gradio.app/docs](https://www.gradio.app/docs)

---

# 13. Where can I learn more about LLMs, agents, and MCP?

Free resources to go deeper after this course:

* Anthropic's Model Context Protocol intro: [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction)
* OpenAI Platform Docs: [https://platform.openai.com/docs](https://platform.openai.com/docs)
* Anthropic API Docs: [https://docs.anthropic.com/](https://docs.anthropic.com/)
* Prompt Engineering Guide: [https://www.promptingguide.ai/](https://www.promptingguide.ai/)

---

# 14. How to contact if I am completely stuck?

If you are stuck and need help, please contact me directly through email
link2rahul@outlook.com. I will do my best to respond promptly but expect
some delay as there are 1000s of students taking my courses.

You can also connect on LinkedIn: [https://www.linkedin.com/in/link2rahul/](https://www.linkedin.com/in/link2rahul/)
and message me directly, or subscribe to my YouTube channel:
[https://www.youtube.com/@propel8](https://www.youtube.com/@propel8)

For any help / suggestions / feedback please do not hesitate to reach out.
I will keep this course updated with new material to address your feedback
and suggestions.

---

# Final Advice

Do not worry about learning every tool immediately.

Focus first on:

* Getting `uv sync` working and one script running end-to-end
* Understanding the flow: LLM call → context → tool calling → MCP → agents
* Reading the code in each part before moving to the next
* Practicing regularly

The tools and workflows become easier as you gain experience.
