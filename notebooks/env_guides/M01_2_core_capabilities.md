# M01_2_core_capabilities.ipynb — 환경 설치·구축·실행 가이드

> 1주차 실습: Agent 의 **4가지 핵심 역량(Tool Use / Memory / Planning / Reasoning)** 을
> 실제 LLM 과 LangGraph 로 단계별 실습합니다. `M01_1_intro.ipynb` 다음에 진행하세요.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비(uv 설치 → `uv venv` → `uv sync` → 커널 등록)는 [README.md](README.md) 를 먼저 따라 하세요.
- `M01_1_intro.ipynb` 를 완료해 `notebooks/.env` 가 만들어져 있어야 합니다.

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langgraph`, `langchain`, `langchain-core`, `pydantic` (노트북 첫 셀의 `utils.uv_install()` 이 자동 설치) |
| 로컬 LLM | **Ollama** 서버 + **`qwen3:8b`** 모델 (네이티브 도구 호출 지원 → Tool Use/ReAct 실습에 필요) |
| 공통 라이브러리 | `agentic_lib`(tools·memory·planning·react·bootstrap·**capabilities**) — 이미 저장소에 포함 |
| (선택) 클라우드 비교 | `GOOGLE_API_KEY` (Gemini 무료 티어) · `NVIDIA_API_KEY` (NVIDIA build 무료 크레딧, §0-B 셀이 커넥터 자동 설치) |

> **왜 `qwen3:8b` 인가**: 이 노트북은 `bind_tools` / `create_react_agent` 로 **도구 호출**을
> 적극 사용합니다. 너무 작은 모델은 도구 호출 JSON 을 안정적으로 만들지 못하므로,
> 도구 호출이 가능한 8B 급 모델을 기본값으로 권장합니다.

## 2. 로컬 LLM 준비 (기본값)

```bat
REM Ollama 설치 (1회)
winget install --id Ollama.Ollama -e

REM 서버 실행 (자동 실행 안 되면 수동으로)
ollama serve

REM 모델 다운로드 (약 5GB, 1회)
ollama pull qwen3:8b

REM 동작 확인
curl.exe http://localhost:11434/api/tags
```

## 3. `.env` 설정

`notebooks/.env` 를 아래처럼 둡니다(없으면 `copy .env.example .env` 로 생성).

```ini
# notebooks/.env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
# 클라우드 무료 API 와 비교하려면 위를 google/nvidia 로 바꾸고 아래 키를 채우세요.
GOOGLE_API_KEY=
NVIDIA_API_KEY=
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
```

> **로컬 ↔ 클라우드 전환**: `.env` 의 `LLM_PROVIDER` 만 `ollama` ↔ `google` ↔ `nvidia` 로 바꾸면 됩니다.
> 노트북 코드는 한 줄도 고치지 않습니다(`utils.get_llm()` 이 공급자 차이를 흡수,
> `bootstrap.to_text()` 가 응답 형식/`<think>` 차이를 흡수). NVIDIA 는 §0-B 셀에서 개별 호출도 가능합니다.

## 4. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - **0. 환경 설정**: `utils.reload_env()` + `agentic_lib` import + 패키지 설치 + 연결 테스트
   - **0-B. (선택) NVIDIA build**: `get_llm('nvidia')` 로 클라우드 모델 개별 호출(키 없으면 안내만)
   - **1. Tool Use**: `@tool` / `bind_tools` / 자동 도구 루프 (`tool_list`, `tool_map`)
   - **2. Memory**: 메시지 히스토리 단기 기억 → LangGraph `MemorySaver` 장기 기억(thread_id)
   - **3. Planning**: `with_structured_output(ExecutionPlan)` → `execute_plan` 으로 자동 실행
   - **4. Reasoning**: Chain of Thought, `create_react_agent`
   - **5. 통합 에이전트**: 4가지 역량 결합
3. 첫 LLM 호출 시 Ollama 가 모델을 메모리에 올리느라 수십 초 걸릴 수 있습니다(이후 빠름).

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `Connection refused (11434)` | Ollama 서버 미실행 → `ollama serve` |
| `model 'qwen3:8b' not found` | 모델 미설치 → `ollama pull qwen3:8b` |
| `tool_calls` 가 비어 있음 / 도구 호출 실패 | 모델이 너무 작거나 도구 호출 미지원 → `qwen3:8b` 같은 도구 호출 가능 모델 사용 |
| 출력에 `<think>...</think>` / `[{'type':'text',...}]` 가 보임 | 노트북은 `bootstrap.to_text()` 로 자동 정규화. 직접 `print(resp.content)` 한 곳이 없는지 확인 |
| 구조화 출력(Planning) 오류 | `with_structured_output` 미지원/불안정 모델일 수 있음 → `qwen3:8b` 또는 `google` 로 비교 |
| 응답이 매우 느림 | 첫 호출은 모델 로딩 시간 포함. GPU 가 있으면 자동 사용 |

## 6. 명령 요약 (복붙용)

```bat
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
cd notebooks && copy .env.example .env
REM .env 에서 LLM_PROVIDER=ollama 확인 후 Jupyter 실행
uv run jupyter notebook
```
