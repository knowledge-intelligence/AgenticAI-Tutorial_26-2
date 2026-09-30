# M02_2_function_calling_eng.ipynb — Environment Setup, Build & Run Guide

> Supplementary notebook: **a 4-way comparison of function-calling reliability across models and providers**. The NVIDIA build default model and
> three free OpenRouter models are called N times (N=10) with the same request, to quantitatively show that whether tool calling succeeds
> depends not only on **model size** but also on **model characteristics** and **provider availability**.
> Referenced from §7 of `M02_3_mcp_a2a_eng.ipynb`.

## 0. Prerequisites

- Windows 11 + CMD + Python 3.11 (uv). For the common setup, see [README_eng.md](README_eng.md).
- Everything is called through cloud APIs, so no local server or model download is needed.

## 1. Requirements

| Category | Details |
|---|---|
| Python packages | `langchain`, `langchain-openai`, `langchain-nvidia-ai-endpoints`, `openai` (installed automatically by the environment cell) |
| Keys | `NVIDIA_API_KEY` (NVIDIA build) and `OPENROUTER_API_KEY` (OpenRouter) — these two are all you need |

### Models compared

| # | Provider · Model | What to look for |
|---|---|---|
| ① | **NVIDIA build** · `deepseek-ai/deepseek-v4.1-flash` (default) | Fixed model, so high reproducibility; fast; supports parallel tool calls |
| ② | **OpenRouter** · `liquid/lfm-2.5-2.6b:free` (small, 2.6B) | Whether even a small model produces spec-compliant `tool_calls` |
| ③ | **OpenRouter** · `nvidia/nemotron-3-super-120b-a12b:free` (large) | Produces valid calls, but whether it tends to call only one tool per response |
| ④ | **OpenRouter** · `openrouter/free` (router) | High availability, but whether the responding model changes on every call |

## 2. Installation (CMD)

The notebook installs Python packages automatically via `utils.uv_install([...])`. To install them manually, run:

```bat
uv pip install langchain langchain-openai langchain-nvidia-ai-endpoints openai
```

## 3. `.env`

Only the two keys are needed in `notebooks/.env`. Comparison models ②–④ are specified directly in the notebook code,
so the notebook runs regardless of the `OPENROUTER_MODEL` value.

```ini
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash   # used in experiment ①
OPENROUTER_API_KEY=sk-or-...
```

> OpenRouter free models are limited to 50 requests per day. This notebook calls OpenRouter dozens of times through experiments ②–④ (10 runs each)
> and the §8 measurement, so running it several times on the same day may hit the limit (`429`).
> To stay under the per-minute limit, the notebook waits `OR_PAUSE` (3 seconds by default) between OpenRouter calls and retries 429 automatically (`max_retries=5`). As a result, it takes a few minutes to run.

## 4. Run order

1. Select the `Agentic AI (uv)` kernel
2. Run from top to bottom:
   - §0 environment cell → §1 comparison models & model factory (`make_llm`) → §2 tools/classifier cell (`TOOL_OK` / `MALFORMED` / `NO_TOOL` / `ERROR`)
   - §3 Experiment ① NVIDIA `deepseek-v4.1-flash` ★default
   - §4 Experiment ② OpenRouter small `lfm-2.5-2.6b` · §5 Experiment ③ OpenRouter large `nemotron-3-super-120b` (model-size axis)
   - §6 Experiment ④ OpenRouter `openrouter/free` (provider-availability axis) → §6-1 real tool execution loop
   - §7 comparison results (4-way) → §8 multi (parallel) function calling measurement (N=8) → §9 summary
3. NVIDIA build is accessed via `ChatNVIDIA`, and OpenRouter via `ChatOpenAI(base_url="https://openrouter.ai/api/v1")`.
   Switching models within OpenRouter only requires changing the one-line `model` string.
4. Free-model results vary with time of day and load, so check the numbers in the table yourself on every run.

## 5. Common issues

| Symptom | Cause / Fix |
|---|---|
| Many `ERROR`s in experiments ② and ③ | The pinned `:free` model is overloaded (`503 provider_overloaded`) or the request limit (`429`) was hit. This is exactly what the provider-availability axis is meant to show; for real use, `OPENROUTER_MODEL=openrouter/free` is recommended |
| Experiment ④'s responding model differs every time | `openrouter/free` is a router that picks an available free model per request, so this is expected (reproducibility is low) |
| The large model calls only one of the two tools | A tendency of `nemotron-3-super-120b`. Running the agent loop several times eventually handles both, but the number of round trips increases |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g., `deepseek-ai/deepseek-v4.1-flash`) |
| `401 Unauthorized` | `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` in `.env` is missing or has a typo |
| `<think>` appears in the output | Some models output their reasoning process as well. Clean it up for display with `bootstrap.to_text()` |

## 6. Command summary (copy & paste)

```bat
REM Check NVIDIA_API_KEY / OPENROUTER_API_KEY in .env
uv pip install langchain langchain-openai langchain-nvidia-ai-endpoints openai
REM Then run the notebook cells from top to bottom (no local server needed)
```
