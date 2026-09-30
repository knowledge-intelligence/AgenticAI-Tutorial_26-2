# M01_2_core_capabilities_eng.ipynb — Environment Installation, Setup & Run Guide

> Week 1 lab: Hands-on, step-by-step practice of the Agent's **4 core capabilities (Tool Use / Memory / Planning / Reasoning)**
> with a real LLM and LangGraph. Do this after `M01_1_intro_eng.ipynb`.

## 0. Prerequisites

- Windows 11 + **CMD (`cmd.exe`)** + Python **3.11** (managed by `uv`)
- Follow the one-time common setup (install uv → `uv venv` → `uv sync` → register the kernel) in [README_eng.md](README_eng.md) first.
- You must have completed `M01_1_intro_eng.ipynb` so that `notebooks/.env` exists.

## 1. What This Notebook Needs

| Category | Details |
|---|---|
| Python packages | `langgraph`, `langchain`, `langchain-core`, `pydantic` (installed automatically by `utils.uv_install()` in the notebook's first cell), `langchain-nvidia-ai-endpoints` (installed automatically by the §0-B cell) |
| Default LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): supports native tool calling and parallel tool calls |
| Shared library | `agentic_lib` (tools · memory · planning · react · bootstrap · **capabilities**) — already included in the repository |
| (Optional) Comparison | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini free tier) |

> **Why `deepseek-v4.1-flash`**: This notebook makes heavy use of **tool calling** via `bind_tools` / `create_react_agent`.
> This model is fast (1–2 seconds), produces tool-call JSON reliably, and can call multiple tools **in parallel**
> in a single response, so it is used as the default. The ReAct and unified-agent cells also use the default `llm`
> as-is, without any separate model configuration.

## 2. Preparing API Keys

Reuse the keys you obtained in `M01_1`. If you don't have them yet, follow §2 of [M01_1_intro_eng.md](M01_1_intro_eng.md)
to get an `NVIDIA_API_KEY` (`nvapi-...`) from [build.nvidia.com](https://build.nvidia.com), and, if you also want to compare,
an `OPENROUTER_API_KEY` (`sk-or-...`) from [openrouter.ai](https://openrouter.ai).

## 3. `.env` Configuration

Set up `notebooks/.env` as shown below (if it doesn't exist, create it with `copy .env.example .env`).

```ini
# notebooks/.env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
# To compare with OpenRouter, change LLM_PROVIDER above to openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

> **Switching providers**: Just change `LLM_PROVIDER` in `.env` between `nvidia` ↔ `openrouter` (or `google`) and re-run from the §0 cell.
> Not a single line of notebook code changes (`utils.get_llm()` absorbs provider differences, and
> `bootstrap.to_text()` absorbs differences in response format / `<think>`). The NVIDIA model can also be called individually in the §0-B cell.

## 4. Execution Order

1. In Jupyter, select the kernel **`Agentic AI (uv)`**
2. Run the cells in order from the top
   - **0. Environment setup**: `utils.reload_env()` + `agentic_lib` imports + package installation + connection test
   - **0-B. Direct NVIDIA build call**: call the default model individually with `get_llm('nvidia')` (only guidance is printed if there is no key)
   - **1. Tool Use**: `@tool` / `bind_tools` / automatic tool loop (`tool_list`, `tool_map`)
   - **2. Memory**: short-term memory with message history → long-term memory with LangGraph `MemorySaver` (thread_id)
   - **3. Planning**: `bind_tools([ExecutionPlan])` + `PydanticToolsParser` (structured output by calling the schema as a tool) → automatic execution with `execute_plan`
   - **4. Reasoning**: Chain of Thought, `create_react_agent`
   - **5. Unified agent**: combining the 4 capabilities
3. Since these are cloud APIs there is no model-loading wait. If you switch to OpenRouter (`openrouter/free`), the responding model may change on each call, so results may vary slightly.

## 5. Common Issues

| Symptom | Cause / Fix |
|---|---|
| `401 Unauthorized` | `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` in `.env` is missing or mistyped, or NVIDIA credits are exhausted |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the request limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free` |
| `tool_calls` is empty / tool call fails | The model may not support tool calling. Switch back to the default `nvidia` + `deepseek-ai/deepseek-v4.1-flash` and compare |
| `<think>...</think>` / `[{'type':'text',...}]` appears in the output | The notebook normalizes these automatically with `bootstrap.to_text()`. Check that there is no place that calls `print(resp.content)` directly |
| Structured output (Planning) error | `ChatNVIDIA.with_structured_output()` sends the `guided_json` parameter, which causes `[400] unknown field` on deepseek. To avoid this, the notebook uses the tool-calling approach (`bind_tools` + `PydanticToolsParser`). If `plan` is `None`, re-run the cell. |

## 6. Command Summary (copy & paste)

```bat
cd notebooks && copy .env.example .env
REM Enter NVIDIA_API_KEY in .env, confirm LLM_PROVIDER=nvidia, then launch Jupyter
uv run jupyter notebook
```
