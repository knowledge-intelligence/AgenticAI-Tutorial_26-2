# Environment Installation & Setup Guides (env_guides)

This folder collects the **per-notebook environment installation, setup, and run command** documents. Before
running each notebook, read its guide first and prepare the environment.

> Execution environment assumptions (fixed target for this course)
>
> | Item | Value |
> |---|---|
> | OS | **Windows 11** |
> | Shell | **CMD (`cmd.exe`)** — not PowerShell/bash |
> | Python | **3.11** (fixed, managed by `uv`) |
> | Default LLM | **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`** (comparison target: **OpenRouter + `openrouter/free`**) |
>
> All shell commands are written in **CMD syntax** (line continuation `^`, environment variables `set NAME=val` / `%NAME%`,
> home directory `%USERPROFILE%`, HTTP checks with `curl.exe`).

## One-Time Common Setup (shared by all notebooks)

The following is a common setup you only need to do once. Each per-notebook guide describes only what is
needed **in addition** to this.

```bat
REM 1) Install uv (once, via PowerShell — the uv install script is PowerShell-only)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

REM 2) Create the virtual environment + install base packages (from the project root)
uv venv --python 3.11
uv sync

REM 3) Register the Jupyter kernel
uv run python -m ipykernel install --user --name=agentic-ai-venv --display-name "Agentic AI (uv)"

REM 4) Launch Jupyter
uv run jupyter notebook notebooks/
```

## Default LLM = NVIDIA build + deepseek-v4.1-flash

This course uses **two free cloud APIs** with no local GPU or local server. Both services provide
an OpenAI-compatible `/v1` endpoint, and changing just the single `LLM_PROVIDER` line in `notebooks/.env`
makes `utils.get_llm()` return the appropriate connector, so the notebook code stays unchanged.

| Provider | `LLM_PROVIDER` | Default model | Connector / Endpoint | Characteristics |
|---|---|---|---|---|
| **NVIDIA build** (default) | `nvidia` | `deepseek-ai/deepseek-v4.1-flash` | `ChatNVIDIA` (`langchain-nvidia-ai-endpoints`) · `https://integrate.api.nvidia.com/v1` | Free credits, fast responses (1-2 s), parallel calls to multiple tools in a single response |
| **OpenRouter** (comparison) | `openrouter` | `openrouter/free` | `ChatOpenAI(base_url="https://openrouter.ai/api/v1")` | Router that automatically selects a free model; the responding model may change on every call |

### Getting Keys

- **NVIDIA build**: Sign in at [build.nvidia.com](https://build.nvidia.com) → model page → `Get API Key` → copy the `nvapi-...` key (free credits provided).
- **OpenRouter**: Sign in at [openrouter.ai](https://openrouter.ai) → `Keys` → `Create Key` → copy the `sk-or-...` key.
  Free models are limited to **50 requests per day**; after topping up 10 or more credits you can use up to **1,000 requests per day**.

`notebooks/.env` configuration (copy `.env.example`, then edit):

```bat
cd notebooks
copy .env.example .env
```

```ini
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
GOOGLE_API_KEY=        # (Optional) only needed when switching to google for comparison
```

> To compare with OpenRouter, change it to `LLM_PROVIDER=openrouter`. Google Gemini (`google`, issued for free at
> [aistudio.google.com](https://aistudio.google.com)), Anthropic, and OpenAI are optional.
>
> `utils.get_llm()` still includes providers for local servers (`ollama`, `llamacpp`, `vllm`), but they are not used in this course.

### Common Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| `401 Unauthorized` | `NVIDIA_API_KEY` (`nvapi-...`) / `OPENROUTER_API_KEY` (`sk-or-...`) in `.env` not set or mistyped, or NVIDIA credits exhausted |
| OpenRouter `503 provider_overloaded` / `429` | The pinned `:free` model is overloaded or the rate limit was exceeded. Change to `OPENROUTER_MODEL=openrouter/free`, and if you exceeded the daily limit (50 requests), retry the next day |
| NVIDIA response is an empty string | Thinking (reasoning) mode was on and all tokens were spent on reasoning. `utils.get_llm('nvidia')` disables thinking mode by default (`NVIDIA_THINKING=false`). If you changed it to `true` in `.env`, revert it. |
| Edited `.env` but changes are not applied | Re-run the notebook's setup cell (`utils.reload_env()`) or restart the kernel |

## Per-Notebook Guides

| Notebook | Guide |
|---|---|
| `M01_1_intro_eng.ipynb` | [M01_1_intro_eng.md](M01_1_intro_eng.md) |
| `M01_2_core_capabilities_eng.ipynb` | [M01_2_core_capabilities_eng.md](M01_2_core_capabilities_eng.md) |
| `M02_0_free_llm_api_eng.ipynb` | [M02_0_free_llm_api_eng.md](M02_0_free_llm_api_eng.md) |
| `M02_1_local_llm_eng.ipynb` | [M02_1_local_llm_eng.md](M02_1_local_llm_eng.md) |
| `M02_2_function_calling_eng.ipynb` | [M02_2_function_calling_eng.md](M02_2_function_calling_eng.md) |
| `M02_3_mcp_a2a_eng.ipynb` | [M02_3_mcp_a2a_eng.md](M02_3_mcp_a2a_eng.md) |
| `M02_4_fastmcp_eng.ipynb` | [M02_4_fastmcp_eng.md](M02_4_fastmcp_eng.md) |
| `M02_5_a2a_multiagent_eng.ipynb` | [M02_5_a2a_multiagent_eng.md](M02_5_a2a_multiagent_eng.md) |
| `M02_6_langgraph_multiagent_eng.ipynb` | [M02_6_langgraph_multiagent_eng.md](M02_6_langgraph_multiagent_eng.md) |
