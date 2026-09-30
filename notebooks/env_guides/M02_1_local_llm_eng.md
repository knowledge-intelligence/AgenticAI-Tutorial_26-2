# M02_1_local_llm_eng.ipynb — Environment Installation, Setup & Run Guide

> Module 1 (weeks 2-4) **Part A**: **OpenAI-compatible LLM API connectivity**. Connect to two free cloud LLMs
> (**Path 1: NVIDIA build** / **Path 2: OpenRouter**) through the **OpenAI-compatible API** (`/v1`) and check their responses.
> Both services are accessed with the same `ChatOpenAI` code, changing only `base_url`, key, and model.
> Tools, MCP, and A2A are covered in Part B (`M02_3_mcp_a2a_eng.ipynb`).
> The file name is the same as in the previous course, but no local server installation or model download is needed.

## 0. Prerequisites

- Windows 11 + **CMD (`cmd.exe`)** + Python **3.11** (managed by `uv`)
- First follow the one-time common setup in [README_eng.md](README_eng.md) (install uv → `uv venv` → `uv sync` → register kernel).
- For how to get the keys, see [M02_0_free_llm_api_eng.md](M02_0_free_llm_api_eng.md).

## 1. What This Notebook Needs

| Category | Details |
|---|---|
| Python packages | `langchain`, `langchain-openai`, `langchain-nvidia-ai-endpoints`, `openai`, `requests` (installed automatically by the setup cell via `utils.uv_install()`) |
| Path 1 | **NVIDIA build** · `https://integrate.api.nvidia.com/v1` · `deepseek-ai/deepseek-v4.1-flash` (requires `NVIDIA_API_KEY`) |
| Path 2 | **OpenRouter** · `https://openrouter.ai/api/v1` · `openrouter/free` (requires `OPENROUTER_API_KEY`) |

> This notebook runs both paths explicitly, **regardless of** the `LLM_PROVIDER` value in `.env`.
> Each path's key, model, and endpoint come from the `NVIDIA_*` / `OPENROUTER_*` values in `.env`; if the model and endpoint
> are not specified separately, the defaults in the table above apply.

## 2. What Each Path Does

| Step | Details |
|---|---|
| (1) Connection test | Call `GET {base_url}/models` with `Authorization: Bearer <key>` to verify connectivity and authentication, and check whether the configured model is in the list |
| (2) Response test | Send the same question with `ChatOpenAI(base_url=..., api_key=..., model=...)` and check the OpenAI-compatible response |

The code for both paths is identical; only `base_url`, key, and model differ. This is the key benefit of the **OpenAI-compatible protocol**.
In other notebooks, `utils.get_llm()` returns the NVIDIA-specific connector `ChatNVIDIA`, but the interface (`.invoke()`) is the same.

To run the connection test directly from CMD, call it as follows (replace the keys with your own).

```bat
curl.exe -H "Authorization: Bearer nvapi-..." https://integrate.api.nvidia.com/v1/models
curl.exe -H "Authorization: Bearer sk-or-..." https://openrouter.ai/api/v1/models
```

## 3. `.env` Configuration

Copy `notebooks/.env.example` to create `notebooks/.env` and set it up as follows.

```bat
cd notebooks
copy .env.example .env
```

```ini
# notebooks/.env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

> **Switching providers**: In other notebooks, just change `LLM_PROVIDER` in `.env` between `nvidia` ↔ `openrouter`.
> Both providers are OpenAI-compatible `/v1`, so they are used the same way through `utils.get_llm()`.

## 4. Execution Order

1. In Jupyter, select the **`Agentic AI (uv)`** kernel
2. Run the cells in order from the top
   - setup (self-contained) → §1 common helpers (`connection_test`, `response_test`)
   - §2 Path 1: NVIDIA build connection test → response test
   - §3 Path 2: OpenRouter connection test → response test (check the model chosen by the router in the `Response model` output)
   - §4 Summary: check the connection status of both paths and whether the configured models are available, side by side
3. Continue with the tools, MCP, and A2A exercises in **Part B** (`M02_3_mcp_a2a_eng.ipynb`).

## 5. Common Issues

| Symptom | Cause / Fix |
|---|---|
| Connection test `401` | Key not set or typo. Check `NVIDIA_API_KEY` (`nvapi-...`) / `OPENROUTER_API_KEY` (`sk-or-...`) in `.env`, then re-run the setup cell |
| Connects but warns `configured model not found` | Typo in `NVIDIA_MODEL` / `OPENROUTER_MODEL`, or the model was taken down by the service. Check the exact name on the model page |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the rate limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free`, and if you exceeded the daily limit (50 requests), retry the next day |
| OpenRouter response model differs every time | Expected behavior: `openrouter/free` is a router that picks an available free model for each request |
| `<think>...</think>` appears in the output | Some models output their reasoning process as well. The notebook removes it automatically with `bootstrap.to_text()` |

## 6. Command Summary (copy & paste)

```bat
REM Prepare .env (enter NVIDIA_API_KEY, OPENROUTER_API_KEY)
cd notebooks && copy .env.example .env

REM (Optional) Check connectivity to both endpoints from CMD
curl.exe -H "Authorization: Bearer nvapi-..." https://integrate.api.nvidia.com/v1/models
curl.exe -H "Authorization: Bearer sk-or-..." https://openrouter.ai/api/v1/models

REM Launch Jupyter
uv run jupyter notebook
```
