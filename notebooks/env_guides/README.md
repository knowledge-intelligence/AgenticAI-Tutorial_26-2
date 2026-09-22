# 환경 설치·구축 가이드 (env_guides)

이 폴더에는 **노트북별 환경 설치·구축·실행 명령** 문서를 모아 둡니다. 각 노트북을
실행하기 전에 해당 가이드를 먼저 읽고 환경을 준비하세요.

> 실행 환경 전제 (본 강의 고정 타깃)
>
> | 항목 | 값 |
> |---|---|
> | OS | **Windows 11** |
> | 셸 | **CMD (`cmd.exe`)** — PowerShell/bash 아님 |
> | Python | **3.11** (고정, `uv` 로 관리) |
> | 기본 LLM | **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`** (비교 대상: **OpenRouter + `openrouter/free`**) |
>
> 모든 셸 명령은 **CMD 문법**으로 작성합니다(줄바꿈 `^`, 환경변수 `set NAME=val` / `%NAME%`,
> 홈 디렉터리 `%USERPROFILE%`, HTTP 점검 `curl.exe`).

## 공통 1회 준비 (모든 노트북 공통)

아래는 한 번만 하면 되는 공통 셋업입니다. 노트북별 가이드는 이 위에 **추가로**
필요한 것만 설명합니다.

```bat
REM 1) uv 설치 (PowerShell 로 1회만 — uv 설치 스크립트가 PowerShell 전용)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

REM 2) 가상환경 생성 + 기본 패키지 설치 (프로젝트 루트에서)
uv venv --python 3.11
uv sync

REM 3) Jupyter 커널 등록
uv run python -m ipykernel install --user --name=agentic-ai-venv --display-name "Agentic AI (uv)"

REM 4) Jupyter 실행
uv run jupyter notebook notebooks/
```

## 기본 LLM = NVIDIA build + deepseek-v4.1-flash

본 강의는 로컬 GPU나 로컬 서버 없이 **무료 클라우드 API 두 가지**를 사용합니다. 두 서비스 모두
OpenAI 호환 `/v1` 엔드포인트를 제공하며, `notebooks/.env` 의 `LLM_PROVIDER` 한 줄만 바꾸면
`utils.get_llm()` 이 알맞은 커넥터를 돌려주므로 노트북 코드는 그대로 둡니다.

| 공급자 | `LLM_PROVIDER` | 기본 모델 | 커넥터 / 엔드포인트 | 특징 |
|---|---|---|---|---|
| **NVIDIA build** (기본) | `nvidia` | `deepseek-ai/deepseek-v4.1-flash` | `ChatNVIDIA`(`langchain-nvidia-ai-endpoints`) · `https://integrate.api.nvidia.com/v1` | 무료 크레딧, 빠른 응답(1~2초), 한 응답에서 여러 도구 병렬 호출 |
| **OpenRouter** (비교) | `openrouter` | `openrouter/free` | `ChatOpenAI(base_url="https://openrouter.ai/api/v1")` | 무료 모델 자동 선택 라우터, 호출마다 응답 모델이 바뀔 수 있음 |

### 키 발급

- **NVIDIA build**: [build.nvidia.com](https://build.nvidia.com) 로그인 → 모델 페이지 → `Get API Key` → `nvapi-...` 키 복사(무료 크레딧 제공).
- **OpenRouter**: [openrouter.ai](https://openrouter.ai) 로그인 → `Keys` → `Create Key` → `sk-or-...` 키 복사.
  무료 모델은 **하루 50요청**으로 제한되며, 크레딧을 10 이상 충전하면 **하루 1,000요청**까지 쓸 수 있습니다.

`notebooks/.env` 설정 (`.env.example` 복사 후 편집):

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
GOOGLE_API_KEY=        # (선택) google 로 비교 전환 시에만 필요
```

> OpenRouter 와 비교하려면 `LLM_PROVIDER=openrouter` 로 바꾸면 됩니다. Google Gemini(`google`,
> [aistudio.google.com](https://aistudio.google.com) 에서 무료 발급), Anthropic, OpenAI 는 선택 사항입니다.
>
> `utils.get_llm()` 에는 로컬 서버용 공급자(`ollama`, `llamacpp`, `vllm`)도 남아 있지만, 본 강의에서는 사용하지 않습니다.

### 공통 문제 해결

| 증상 | 원인/해결 |
|---|---|
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY`(`nvapi-...`) / `OPENROUTER_API_KEY`(`sk-or-...`) 미설정·오타, 또는 NVIDIA 크레딧 소진 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경하고, 하루 한도(50요청)를 넘었으면 다음 날 재시도 |
| NVIDIA 응답이 빈 문자열 | 사고(추론) 모드가 켜져 토큰을 추론에 다 쓴 경우입니다. `utils.get_llm('nvidia')` 는 기본으로 사고 모드를 끕니다(`NVIDIA_THINKING=false`). `.env` 에서 `true` 로 바꿨다면 되돌리세요. |
| `.env` 를 고쳤는데 반영 안 됨 | 노트북의 setup 셀(`utils.reload_env()`)을 다시 실행하거나 커널을 재시작 |

## 노트북별 가이드

| 노트북 | 가이드 |
|---|---|
| `M01_1_intro.ipynb` | [M01_1_intro.md](M01_1_intro.md) |
| `M01_2_core_capabilities.ipynb` | [M01_2_core_capabilities.md](M01_2_core_capabilities.md) |
| `M02_0_free_llm_api.ipynb` | [M02_0_free_llm_api.md](M02_0_free_llm_api.md) |
| `M02_1_local_llm.ipynb` | [M02_1_local_llm.md](M02_1_local_llm.md) |
| `M02_2_function_calling.ipynb` | [M02_2_function_calling.md](M02_2_function_calling.md) |
| `M02_3_mcp_a2a.ipynb` | [M02_3_mcp_a2a.md](M02_3_mcp_a2a.md) |
| `M02_4_fastmcp.ipynb` | [M02_4_fastmcp.md](M02_4_fastmcp.md) |
| `M02_5_a2a_multiagent.ipynb` | [M02_5_a2a_multiagent.md](M02_5_a2a_multiagent.md) |
| `M02_6_langgraph_multiagent.ipynb` | [M02_6_langgraph_multiagent.md](M02_6_langgraph_multiagent.md) |
