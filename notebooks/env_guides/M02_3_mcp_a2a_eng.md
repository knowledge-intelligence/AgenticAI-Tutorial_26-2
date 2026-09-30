# M02_3_mcp_a2a_eng.ipynb — Environment Setup, Build & Run Guide

> Module 1 (Weeks 2–4) **Part B**: **Tools · MCP · A2A**. Hands-on practice with LangChain tool definitions,
> the MCP (Model Context Protocol) architecture, the three A2A (Agent-to-Agent) patterns (hierarchical / sequential / peer-to-peer),
> and the Individual Tool Agent. Verify your OpenAI-compatible LLM API connection first in **Part A**
> (`M02_1_local_llm_eng.ipynb`).
> The default LLM is **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`** (supports native and parallel tool calling).

## 0. Prerequisites

- Windows 11 + **CMD (`cmd.exe`)** + Python **3.11** (managed by `uv`)
- Follow [README_eng.md](README_eng.md) first for the one-time common setup (install uv → `uv venv` → `uv sync` → register the kernel).
- For API key preparation and connection checks, see [M02_1_local_llm_eng.md](M02_1_local_llm_eng.md).
  This notebook uses `LLM_PROVIDER` from `.env` as is (`utils.get_llm()`, default `nvidia`).

## 1. What this notebook needs

| Category | Details |
|---|---|
| Python packages | `langchain`, `langchain-openai`, `langchain-community`, `langchain-google-genai`, `langchain-anthropic`, `openai`, `requests`, `ddgs` (installed automatically by the setup cell via `utils.uv_install()`) |
| Default LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): stable native `tool_calls` for the §7/§8 agents |
| Web search tool | **DuckDuckGo** (`ddgs`) — **network required** for the §4 tools exercise |
| (Optional) comparison | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini free tier) |

## 2. LLM preparation (NVIDIA build)

Since this is a tool-calling exercise, the default is **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`**, which produces stable native `tool_calls`
and can call multiple tools in parallel in a single response. No extra installation is needed — just `NVIDIA_API_KEY`.
If you don't have a key, get one at [build.nvidia.com](https://build.nvidia.com) (skip this if you already did it in Part A).

## 3. Network dependency (web search tool)

The §4 tools exercise performs **real web searches** with `langchain_community.tools.DuckDuckGoSearchRun` (package `ddgs`).
An internet connection is required.

```bat
REM The setup cell installs these automatically, but manual installation also works
uv pip install ddgs langchain-community
```

> If DuckDuckGo is blocked (e.g., **on a corporate network**), you can replace `search` (DuckDuckGo) in the notebook's tool list
> with `tools.search_web` (simulation).

## 4. `.env` configuration

Copy `notebooks/.env.example` to create `notebooks/.env` and set it up as follows.

```bat
cd notebooks
copy .env.example .env
```

```ini
# notebooks/.env (default is NVIDIA build)
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash

# To compare with OpenRouter, change to LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

> **Switching providers**: just change `LLM_PROVIDER` in `.env` between `nvidia` ↔ `openrouter` (or `google`).
> No changes to the notebook code are needed.

## 5. Run order

1. In Jupyter, select the **`Agentic AI (uv)`** kernel
2. Run the cells in order from the top
   - setup (self-contained) → §4 LangChain tools → §5 MCP (Host/Client/Server) → §6 the three A2A patterns
   - §7 LangChain agent (tool calling) → §8 Individual Tool Agent exercise
3. Since it uses cloud APIs, there is no model-loading wait.

## 6. About tool calling (function calling)

- **NVIDIA build + `deepseek-v4.1-flash`** produces stable native `tool_calls` and also supports parallel tool calls, so the §7/§8 agents work as is.
- If you switch to OpenRouter `openrouter/free`, the responding model changes on every call, so tool-calling results may differ from run to run.
  If results are unstable, switch back to `LLM_PROVIDER=nvidia`.
- For the 4-way comparison of tool-calling reliability across models and providers, see the supplementary notebook `M02_2_function_calling_eng.ipynb`.

## 7. Common issues

| Symptom | Cause / Fix |
|---|---|
| `401 Unauthorized` | `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` in `.env` is missing or has a typo (see the Part A guide) |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g., `deepseek-ai/deepseek-v4.1-flash`) |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the request limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free` |
| DuckDuckGo search error / timeout | Network issue. If blocked, you can substitute `tools.search_web` (simulation) |
| `<think>...</think>` appears in the output | Some models output their reasoning process as well. The notebook removes it automatically with `bootstrap.to_text()` |
| Tool calling doesn't work | You switched to a model that is poor at tool calling. Revert to `LLM_PROVIDER=nvidia` + `deepseek-ai/deepseek-v4.1-flash` |

## 8. Command summary (copy & paste)

```bat
REM Prepare the web search tool + .env, then launch Jupyter
uv pip install ddgs langchain-community
cd notebooks && copy .env.example .env
REM Enter NVIDIA_API_KEY in .env and confirm LLM_PROVIDER=nvidia
uv run jupyter notebook
```
