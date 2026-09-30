# M01_1_intro_eng.ipynb — Environment Installation, Setup & Run Guide

> Week 0: Course introduction and environment setup. This notebook sets up, for the first time, the **development environment**
> and the **default LLM (NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`)** used throughout the course.

## 0. Prerequisites

- Windows 11 + **CMD (`cmd.exe`)** + Python **3.11** (managed by `uv`)
- Follow the one-time common setup in [README_eng.md](README_eng.md) first (install uv → `uv venv` → `uv sync` → register the kernel).

## 1. What This Notebook Needs

| Category | Details |
|---|---|
| Python packages | `langchain`, `langchain-openai`, `langchain-google-genai`, `langchain-nvidia-ai-endpoints`, `langgraph`, `python-dotenv` (the §6-B cell installs them automatically if needed) |
| Default LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (requires `NVIDIA_API_KEY`, free credits) |
| Comparison LLM | **OpenRouter** + **`openrouter/free`** (requires `OPENROUTER_API_KEY`, free models) |
| (Optional) Other clouds | `GOOGLE_API_KEY` (Gemini free tier), Anthropic, OpenAI |

## 2. Getting API Keys (Required)

No local installation is needed — you only have to obtain keys for the two free cloud APIs.

- **NVIDIA build**: Log in at [build.nvidia.com](https://build.nvidia.com) → model page → `Get API Key` → `NVIDIA_API_KEY=nvapi-...`
- **OpenRouter**: Log in at [openrouter.ai](https://openrouter.ai) → `Keys` → `Create Key` → `OPENROUTER_API_KEY=sk-or-...`
  (Free models allow 50 requests per day; 1,000 requests per day once you top up 10 or more credits)

## 3. `.env` Configuration

Copy `notebooks/.env.example` to create `notebooks/.env`, and set it up as shown below.

```bat
cd notebooks
copy .env.example .env
```

```ini
# notebooks/.env (default is NVIDIA build)
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
# To compare with OpenRouter, change LLM_PROVIDER above to openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
# (Optional) Google Gemini
GOOGLE_API_KEY=
```

> **Switching providers**: Just change `LLM_PROVIDER` in `.env` between `nvidia` ↔ `openrouter` (or `google`).
> Not a single line of notebook code changes (`utils.get_llm()` absorbs the differences between providers).

## 4. Execution Order

1. In Jupyter, select the kernel **`Agentic AI (uv)`**
2. Run the cells in order from the top
   - Sections 1–2: Check uv/packages
   - Sections 3–6: Choose a provider → test the `get_llm()` connection (`NVIDIA_API_KEY` required)
   - Section 6-B: Connect to and test the free cloud APIs (NVIDIA build · OpenRouter) (only services with a key are called; otherwise only guidance is printed)
   - Sections 7–13: LLM vs Agent, the 4 core capabilities (tools · memory · planning · reasoning), ReAct
3. Since these are cloud APIs there is no model-loading wait; NVIDIA `deepseek-v4.1-flash` usually responds within 1–2 seconds.

## 5. Common Issues

| Symptom | Cause / Fix |
|---|---|
| `401 Unauthorized` | `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` in `.env` is missing or mistyped, or NVIDIA credits are exhausted |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the request limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free` |
| `<think>...</think>` appears in the output | Some models output their thinking process as well. The notebook removes it automatically with `bootstrap.to_text()` |
| Korean text is garbled (`cp949`) | Notebooks (Jupyter) use UTF-8, so they are fine. Only plain CMD output is affected |

## 6. Command Summary (copy & paste)

```bat
cd notebooks && copy .env.example .env
REM Enter NVIDIA_API_KEY / OPENROUTER_API_KEY in .env, confirm LLM_PROVIDER=nvidia, then launch Jupyter
uv run jupyter notebook
```
