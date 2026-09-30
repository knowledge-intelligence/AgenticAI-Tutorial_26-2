# M02_6_langgraph_multiagent_eng.ipynb — Environment Installation, Setup, and Run Guide

> Module 1 (weeks 2-4) **supplement**: **LangGraph multi-agent (Supervisor pattern)**. This re-implements **the same exercise** as [`M02_5_a2a_multiagent_eng.ipynb`](../M02_5_a2a_multiagent_eng.ipynb)
> (calculation, summarization, and writing specialist agents + a coordinator) using **LangGraph**
> `StateGraph` instead of the standard protocol `a2a-sdk`. Each specialist agent is **a node in the graph, not an HTTP server**; delegation is
> expressed with **conditional edges**, and parallel delegation with **`Send` fan-out**.
> For a conceptual introduction, see the three A2A patterns in [`M02_3_mcp_a2a_eng.ipynb`](../M02_3_mcp_a2a_eng.ipynb).
> The LLM is determined by **`LLM_PROVIDER`** in `.env` (`utils.get_llm()`) and serves as the brain of each node (agent).

## 0. Prerequisites

- Windows 11 + **CMD (`cmd.exe`)** + Python **3.11** (managed by `uv`)
- For the one-time common setup, follow [README_eng.md](README_eng.md) first (install uv → `uv venv` → `uv sync` → register kernel).
- For preparing API keys and checking connectivity, see [M02_1_local_llm_eng.md](M02_1_local_llm_eng.md).
  This notebook uses `LLM_PROVIDER` from `.env` as-is (`utils.get_llm()`, default `nvidia`).

## 1. What this notebook needs

| Category | Details |
|---|---|
| Python packages | `langgraph`, `langchain`, `langchain-openai` (installed automatically by the setup cell via `utils.uv_install()`) |
| Default LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): used to generate each specialist node's responses |
| Network | The graph runs within a single process, but LLM calls require an internet connection |
| (Optional) Comparison | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini free tier) |

> **Difference from A2A (`M02_5`)**: A2A launches each agent as an **independent HTTP server** and connects them via a protocol, whereas
> LangGraph declares the collaboration flow (branching, cycles, parallelism) as **a graph within one process**. Server/protocol dependencies
> such as `httpx`/`uvicorn`/`a2a-sdk` are not needed.

## 2. Preparing the LLM (NVIDIA build)

No separate installation is needed; you only need `NVIDIA_API_KEY` in `.env`. If you don't have a key,
get one at [build.nvidia.com](https://build.nvidia.com) (skip this if you already did it for another notebook).

## 3. Installing the LangGraph packages

The setup cell installs them automatically, but manual installation is also possible.

```bat
uv pip install langgraph langchain langchain-openai
```

## 4. `.env` configuration

Copy `notebooks/.env.example` to create `notebooks/.env` and set it up as below.

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

## 5. Run order

1. In Jupyter, select the **`Agentic AI (uv)`** kernel
2. Run the cells in order from the top
   - setup (self-contained) → §1 specialist agents → §2 State → §3 Planner node
   - §4 nodes/router → §5 graph assembly & visualization → §6 execution (streaming) → §7 parallel (`Send`) → §8 wrap-up
3. Each node calls a cloud LLM, so graph execution may take from a few seconds to tens of seconds depending on network conditions.
4. `graph.stream()` emits a `{node_name: state_update}` event each time a node finishes, letting you observe the execution flow as it happens.

## 6. Common issues

| Symptom | Cause / Fix |
|---|---|
| `401 Unauthorized` | `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` in `.env` is missing or has a typo |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the rate limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free` |
| `Graph must have an entrypoint` | Missing entry edge such as `add_edge(START, "planner")`. Already handled in this notebook |
| Conditional edge branching doesn't work | `route_map` must include **all specialist nodes + writer**. Already handled in this notebook |
| Parallel (`Send`) results get overwritten | The `results` channel needs the reducer `Annotated[list, operator.add]`. Already handled in §7 |
| `<think>...</think>` in output | Some models output their reasoning process as well. Removed automatically by `bootstrap.invoke_text()`/`to_text()` |
| Decomposition JSON error | The model may violate the format (especially after switching to `openrouter/free`). Handled safely by the **fallback parser** in `planner_node` |

## 7. Key LangGraph symbols (reference)

| Symbol | Location | Role |
|---|---|---|
| `StateGraph` | `langgraph.graph` | State-based graph builder |
| `START` / `END` | `langgraph.graph` | Entry/exit node constants |
| `add_node` / `add_edge` | `StateGraph` | Register node / fixed edge |
| `add_conditional_edges(src, router, map)` | `StateGraph` | Conditional routing (branching, cycles) |
| `compile()` → `.get_graph().draw_mermaid()` | `StateGraph` | Compile the executable graph / visualize |
| `.stream(state)` / `.invoke(state)` | Compiled graph | Streaming observation / batch execution |
| `Send(node, payload)` | `langgraph.types` | Fan-out (parallel delegation) |
| `Annotated[list, operator.add]` | `typing` | Fan-in of parallel results (reducer) |

## 8. Command summary (copy-paste)

```bat
REM Prepare LangGraph packages + .env, then launch Jupyter
uv pip install langgraph langchain langchain-openai
cd notebooks && copy .env.example .env
REM Enter NVIDIA_API_KEY in .env and confirm LLM_PROVIDER=nvidia
uv run jupyter notebook
```
