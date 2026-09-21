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
> | 기본 LLM | **로컬 Ollama + `qwen3:8b`** (클라우드 `google` 은 비교/대체용) |
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

## 기본 LLM = 로컬 Ollama + qwen3:8b

본 강의는 로컬 LLM 을 기본값으로 사용합니다(무료·오프라인·재현성). 클라우드(Gemini)는
`notebooks/.env` 의 `LLM_PROVIDER` 한 줄만 바꾸면 비교용으로 즉시 전환됩니다.

```bat
REM 1) Ollama 설치 (1회)
winget install --id Ollama.Ollama -e

REM 2) Ollama 서버 실행 (설치 시 자동 실행되기도 함; 안 되면 수동 실행)
ollama serve

REM 3) 모델 다운로드 (약 5GB, 1회)
ollama pull qwen3:8b

REM 4) 동작 확인 (OpenAI 호환 엔드포인트가 11434 포트에 떠 있는지)
curl.exe http://localhost:11434/api/tags
```

`notebooks/.env` 설정 (`.env.example` 복사 후 편집):

```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
GOOGLE_API_KEY=        # google 로 비교 전환 시에만 필요
```

> 클라우드와 비교하려면 `LLM_PROVIDER=google` 로 바꾸고 `GOOGLE_API_KEY` 를 채우세요.
> ([aistudio.google.com](https://aistudio.google.com) 에서 무료 발급)

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
| `M03_1_nemo_guardrails.ipynb` | [M03_1_nemo_guardrails.md](M03_1_nemo_guardrails.md) |
| `M03_2_tracing.ipynb` | [M03_2_tracing.md](M03_2_tracing.md) |
| `M03_3_self_refine.ipynb` | [M03_3_self_refine.md](M03_3_self_refine.md) |
| `M03_4_nemo_agent_toolkit.ipynb` | [M03_4_nemo_agent_toolkit.md](M03_4_nemo_agent_toolkit.md) |
| `M04_1_embeddings.ipynb` | [M04_1_embeddings.md](M04_1_embeddings.md) |
| `M04_2_vector_rag.ipynb` | [M04_2_vector_rag.md](M04_2_vector_rag.md) |
| `M04_3_graph_rag.ipynb` | [M04_3_graph_rag.md](M04_3_graph_rag.md) |
| `M04_4_agent_memory.ipynb` | [M04_4_agent_memory.md](M04_4_agent_memory.md) |
| `M04_5_memory.ipynb` | [M04_5_memory.md](M04_5_memory.md) |
| `M05_1_action.ipynb` | [M05_1_action.md](M05_1_action.md) |
| `M05_2_planning.ipynb` | [M05_2_planning.md](M05_2_planning.md) |
