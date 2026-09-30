# M02_4_fastmcp_eng.ipynb — Environment Setup, Build & Run Guide

> A notebook that builds an **MCP Host · Client · Server** with FastMCP and demonstrates simple tool use.
> It uses the in-memory transport, so the whole flow runs inside a single notebook without separate processes.

## 0. Prerequisites
- Windows 11 + CMD + Python 3.11 (uv). For the common setup, see [README_eng.md](README_eng.md).
- Default LLM = **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`** (acts as the Host). You only need `NVIDIA_API_KEY` in `.env`.

## 1. Requirements
| Category | Details |
|---|---|
| Python packages | `fastmcp` (installed automatically by the notebook's first cell via `utils.uv_install(['fastmcp'])`), `langchain-openai`, `langchain-nvidia-ai-endpoints` |
| LLM | `utils.get_llm()` (default `nvidia` + `deepseek-ai/deepseek-v4.1-flash`, the Host that selects tools) |

## 2. Installation (CMD)
```bat
REM Install FastMCP (manual install). Usually unnecessary because the notebook installs it automatically
uv pip install fastmcp
```

## 3. `.env`
With the default (NVIDIA build), just fill in the key and leave the rest as is.
```ini
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
```

> To compare with OpenRouter, change to `LLM_PROVIDER=openrouter` and fill in `OPENROUTER_API_KEY`.

## 4. Run Order
1. Select the `Agentic AI (uv)` kernel
2. Run from the top:
   - §0 Environment setup (install fastmcp + prepare the LLM)
   - §1 **Server**: define tools with `FastMCP` + `@mcp.tool`
   - §2 **Client**: in-memory connection via `Client(mcp)` → `list_tools` / `call_tool` (top-level `await` in cells)
   - §3 **Host**: the NVIDIA build LLM selects tools → executes them via the Client → final answer
3. §2 and §3 use an `async` API, so `await` is used directly in cells (Jupyter supports top-level await).

## 5. Common Issues
| Symptom | Cause / Fix |
|---|---|
| `ModuleNotFoundError: fastmcp` | Run the first cell `utils.uv_install(['fastmcp'])`, or `uv pip install fastmcp` |
| `RuntimeError: no running event loop` / await errors | Always run in a Jupyter kernel (supports top-level await). In a plain script you need `asyncio.run(...)` |
| Host does not call tools | Confirm you are using `LLM_PROVIDER=nvidia` + `deepseek-ai/deepseek-v4.1-flash`. The OpenRouter router may switch models per call, so results can vary |
| `410 Gone` (NVIDIA) | The model has been retired. Change `NVIDIA_MODEL` to a model currently listed on build.nvidia.com (e.g. `deepseek-ai/deepseek-v4.1-flash`) |
| `<think>` exposed | Add `/no_think` to the prompt and clean up output with `bootstrap.to_text()` |

## 6. Command Summary (copy & paste)
```bat
uv pip install fastmcp
REM Enter NVIDIA_API_KEY in .env and confirm LLM_PROVIDER=nvidia
REM Then run the notebook cells from the top
```
