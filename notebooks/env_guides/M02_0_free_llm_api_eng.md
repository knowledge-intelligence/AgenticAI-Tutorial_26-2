# M02_0_free_llm_api_eng.ipynb — Environment Installation, Setup & Run Guide

> This notebook connects to and tests three free cloud LLM APIs (**Google AI Studio (Gemini)**, **NVIDIA build**, **OpenRouter**).
> The course's default LLM is **NVIDIA build** (`deepseek-ai/deepseek-v4.1-flash`),
> the comparison target is **OpenRouter** (`openrouter/free`), and Google Gemini is optional.
> Because OpenRouter is OpenAI-compatible, both approaches are covered: **calling the OpenRouter SDK (OpenAI SDK) directly** and **connecting via LangChain**.

## 0. Prerequisites
- Windows 11 + CMD + Python 3.11 (uv). For the common setup, see [README_eng.md](README_eng.md).
- Run in the course's default kernel **`Agentic AI (uv)`**.
- `NVIDIA_API_KEY` and `OPENROUTER_API_KEY` are used throughout the course and are **required**; `GOOGLE_API_KEY` is **optional**.
  Only services whose keys are set are actually called; for missing services, only guidance is printed.

## 1. What You Need
| Category | Details |
|---|---|
| Python packages | `langchain-google-genai`, `langchain-nvidia-ai-endpoints`, `openai`, `langchain-openai` (installed automatically by the notebook's first cell) |
| Keys | Required: `NVIDIA_API_KEY` (NVIDIA build), `OPENROUTER_API_KEY` (OpenRouter) · Optional: `GOOGLE_API_KEY` (Gemini) |

## 2. Getting Keys & Configuring `.env`

Fill in the keys below in `notebooks/.env` (copy `.env.example`, then edit). The Google key is not required.

```ini
# Default provider
LLM_PROVIDER=nvidia

# NVIDIA build (free credits, default): https://build.nvidia.com → model page → Get API Key
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
# (Optional) only if you want to change the default endpoint
# NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# OpenRouter (free model router) — https://openrouter.ai → Keys → Create Key
OPENROUTER_API_KEY=sk-or-...
# (Optional) defaults. openrouter/free is a router that automatically selects a free model
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# OPENROUTER_MODEL=openrouter/free

# (Optional) Google AI Studio (free tier): https://aistudio.google.com → Get API Key
GOOGLE_API_KEY=AIza...
```

### How to Get the Keys
- **Google AI Studio**: Sign in at [aistudio.google.com](https://aistudio.google.com) → `Get API Key` → `Create API key` → copy the key.
- **NVIDIA build**: Sign in at [build.nvidia.com](https://build.nvidia.com) → page of the model you want (e.g. `deepseek-ai/deepseek-v4.1-flash`) →
  `Get API Key` (free credits provided) → copy the `nvapi-...` key. Models may be retired without notice (`410 Gone`),
  so when using a different model, check on its model page that it is still available.
- **OpenRouter**: Sign in at [openrouter.ai](https://openrouter.ai) → `Keys` → `Create Key` → copy the `sk-or-...` key.
  New users receive a small free allowance and can test with `openrouter/free`, which automatically selects a free model.
  The free-model limit is **50 requests per day** (**1,000 requests per day** after topping up 10 or more credits). Pinning a specific `:free` model
  often fails due to overload (503) or rate limits (429), so the `openrouter/free` router is recommended.

## 3. Installation (CMD, if done manually)
```bat
uv pip install langchain-google-genai langchain-nvidia-ai-endpoints openai langchain-openai
```
> Usually unnecessary, since the notebook's first cell installs these automatically with `utils.uv_install([...])`.

## 4. Execution Order
1. Select the `Agentic AI (uv)` kernel
2. Run from the top:
   - §0 Environment setup (package installation + key status check)
   - §1 Google Gemini test (`utils.get_llm('google')`)
   - §2 NVIDIA build test (`utils.get_llm('nvidia')` = `ChatNVIDIA`, default `deepseek-ai/deepseek-v4.1-flash`)
   - §3 OpenRouter test — A) OpenRouter SDK (OpenAI SDK), B) LangChain (`utils.get_llm('openrouter')`)
   - §4 Streaming (shared across Google · NVIDIA · OpenRouter), §5 comparison of the three services' responses

## 5. Common Issues
| Symptom | Cause / Fix |
|---|---|
| `[401] Unauthorized` (NVIDIA) | Key not set / typo / credits exhausted. Check `NVIDIA_API_KEY` in `.env` |
| NVIDIA `ReadTimeout` / `503` | Large models are often slow or overloaded. Set `NVIDIA_MODEL` to the default `deepseek-ai/deepseek-v4.1-flash` |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| `key set: False` even though it is in .env | Notebooks auto-load it because CWD=`notebooks/`. When running as a script, run it from `notebooks/` |
| Google response looks like `[{...}]` | Gemini list content — normalized with `bootstrap.to_text()` (the notebook handles this) |
| `model name not found` (NVIDIA) | Check the exact `provider/model` name on each model page at build.nvidia.com |
| `429 Rate limit` (OpenRouter) | Free-model limit exceeded (50 requests/day). Retry later or top up 10+ credits (1,000 requests/day) |
| OpenRouter `503 provider_overloaded` / `429` (specific model) | The pinned `:free` model is overloaded. Change to `OPENROUTER_MODEL=openrouter/free` |
| `401 No auth` (OpenRouter) | Check that `OPENROUTER_API_KEY` (`sk-or-...`) is set and has no typos |

## 6. Command Summary (copy & paste)
```bat
copy .env.example .env
REM Fill in NVIDIA_API_KEY / OPENROUTER_API_KEY in .env (GOOGLE_API_KEY is optional)
uv pip install langchain-google-genai langchain-nvidia-ai-endpoints openai langchain-openai
REM Then run the notebook cells from the top
```
