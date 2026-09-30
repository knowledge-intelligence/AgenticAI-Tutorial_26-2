# M02_5_a2a_multiagent_eng.ipynb — Environment Setup, Build & Run Guide

> Module 1 (weeks 2-4) **supplement**: **A2A protocol multi-agent**. Using the reference implementation **`a2a-sdk` (a2a-python) 1.1.0**,
> specialist agents (calculation, summarization, writing) are launched as real **A2A HTTP servers**, and a **coordinator** decomposes a
> compound request, **delegates via A2A messages** to each agent, and then aggregates the results.
> For the conceptual introduction, first see the three A2A patterns in [`M02_3_mcp_a2a_eng.ipynb`](../M02_3_mcp_a2a_eng.ipynb).
> The default LLM is **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`**, used as the brain of each agent.

## 0. Prerequisites

- Windows 11 + **CMD (`cmd.exe`)** + Python **3.11** (managed by `uv`)
- Follow the one-time common setup in [README_eng.md](README_eng.md) first (install uv → `uv venv` → `uv sync` → register the kernel).
- For API key setup and connection checks, see [M02_1_local_llm_eng.md](M02_1_local_llm_eng.md).
  This notebook uses `LLM_PROVIDER` from `.env` as is (`utils.get_llm()`, default `nvidia`).

## 1. What This Notebook Needs

| Category | Details |
|---|---|
| Python packages | `a2a-sdk` (1.1.0), `uvicorn`, `httpx`, `langchain`, `langchain-openai` (installed automatically by the setup cell via `utils.uv_install()`) |
| Default LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): used to generate each specialist agent's responses |
| Network | A2A servers and clients communicate over **local loopback** (127.0.0.1). LLM calls require an internet connection |
| (Optional) Comparison | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini free tier) |

> `a2a-sdk` provides **protocol-buffer-based types** (`AgentCard`, `Message`, `Task`, etc.) and
> **server (AgentExecutor/DefaultRequestHandler) and client (ClientFactory/A2ACardResolver)** APIs.
> The API differs significantly between versions, so this notebook is written against **1.1.0**.

## 2. LLM Setup (NVIDIA build)

No separate installation is needed; you only need `NVIDIA_API_KEY` in `.env`. If you do not have a key,
get one at [build.nvidia.com](https://build.nvidia.com) (skip if you already did this for another notebook).

## 3. Installing the A2A Packages

The setup cell installs them automatically, but you can also install them manually.

```bat
uv pip install a2a-sdk uvicorn httpx
```

## 4. `.env` Configuration

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

## 5. Run Order

1. In Jupyter, select the **`Agentic AI (uv)`** kernel
2. Run the cells in order from the top
   - setup (self-contained) → §1 imports/helpers → §2 AgentCard definitions → §3 start A2A servers
   - §4 card discovery → §5 single-agent call → §6 coordinator (decompose → delegate → aggregate) → §7 cleanup (shut down servers)
3. Each agent server runs in a **background thread** and automatically picks a random free port (avoids port conflicts).
4. Each agent calls a cloud LLM, so running the coordinator may take from a few seconds to several tens of seconds depending on network conditions.
5. The notebook calls the **async A2A API** with top-level `await` (supported by Jupyter/ipykernel).

## 6. Common Issues

| Symptom | Cause / Fix |
|---|---|
| `401 Unauthorized` | `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` in `.env` is missing or has a typo |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the rate limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free` |
| `started=False` in the server cell | Port readiness is delayed. Re-run the cell or retry after a moment |
| `Agent should enqueue Task before ...` | The executor did not enqueue the Task first. This notebook's `LLMAgentExecutor` prevents this by enqueuing `new_task` first |
| Empty response | Results must be attached as an **Artifact** (`updater.add_artifact`). This notebook already does so |
| `<think>...</think>` in output | Some models output their reasoning process too. `bootstrap.invoke_text()`/`to_text()` removes it automatically |
| Coordinator decomposition JSON error | The model may violate the format (especially when switching to `openrouter/free`). This notebook handles it safely with a **fallback parser** |
| `RuntimeError: event loop ...` | Restart the kernel and re-run from the top in order (servers and clients are created on the same loop) |

## 7. A2A SDK 1.1.0 Key Symbols (reference)

| Symbol | Location | Role |
|---|---|---|
| `AgentCard`/`AgentSkill`/`AgentCapabilities`/`AgentInterface` | `a2a.types` | Agent specification (discovery) |
| `Message`/`Part`/`Role`/`Task`/`TaskState` | `a2a.types` | Protocol message and task types |
| `AgentExecutor`/`RequestContext` | `a2a.server.agent_execution` | Server-side execution model |
| `EventQueue` | `a2a.server.events` | Result event queue |
| `TaskUpdater` | `a2a.server.tasks.task_updater` | Records task status and Artifacts |
| `DefaultRequestHandler` | `a2a.server.request_handlers` | Request handler |
| `InMemoryTaskStore` | `a2a.server.tasks` | Task store (demo) |
| `create_agent_card_routes`/`create_jsonrpc_routes` | `a2a.server.routes` | Starlette routes |
| `ClientFactory`/`ClientConfig`/`A2ACardResolver` | `a2a.client` | Client creation and card discovery |
| `TransportProtocol` | `a2a.utils` | Transport bindings (JSONRPC/GRPC/HTTP_JSON) |
| `new_text_message`/`new_text_part`/`new_task`/`get_stream_response_text` | `a2a.helpers.proto_helpers` | Message/task creation and parsing |

## 8. Command Summary (copy & paste)

```bat
REM Prepare the A2A packages + .env, then launch Jupyter
uv pip install a2a-sdk uvicorn httpx
cd notebooks && copy .env.example .env
REM Enter NVIDIA_API_KEY in .env and confirm LLM_PROVIDER=nvidia
uv run jupyter notebook
```
