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
| Python 패키지 | `langgraph`, `langchain`, `langchain-core`, `pydantic` (노트북 첫 셀의 `utils.uv_install()` 이 자동 설치), `langchain-nvidia-ai-endpoints` (§0-B 셀이 자동 설치) |
| 기본 LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): 네이티브 도구 호출·병렬 도구 호출 지원 |
| 공통 라이브러리 | `agentic_lib`(tools·memory·planning·react·bootstrap·**capabilities**) — 이미 저장소에 포함 |
| (선택) 비교 | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini 무료 티어) |

> **왜 `deepseek-v4.1-flash` 인가**: 이 노트북은 `bind_tools` / `create_react_agent` 로 **도구 호출**을
> 적극 사용합니다. 이 모델은 응답이 빠르고(1~2초), 도구 호출 JSON 을 안정적으로 만들며, 한 응답에서
> 여러 도구를 **병렬로** 호출할 수 있어 기본값으로 사용합니다. ReAct·통합 에이전트 셀도 별도 모델 설정 없이
> 기본 `llm` 을 그대로 씁니다.

## 2. API 키 준비

`M01_1` 에서 발급한 키를 그대로 씁니다. 아직 없다면 [M01_1_intro.md](M01_1_intro.md) 의 §2 를 따라
[build.nvidia.com](https://build.nvidia.com) 에서 `NVIDIA_API_KEY`(`nvapi-...`)를, 비교까지 하려면
[openrouter.ai](https://openrouter.ai) 에서 `OPENROUTER_API_KEY`(`sk-or-...`)를 발급하세요.

## 3. `.env` 설정

`notebooks/.env` 를 아래처럼 둡니다(없으면 `copy .env.example .env` 로 생성).

```ini
# notebooks/.env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
# OpenRouter 와 비교하려면 위 LLM_PROVIDER 를 openrouter 로 바꿈
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

> **공급자 전환**: `.env` 의 `LLM_PROVIDER` 만 `nvidia` ↔ `openrouter` (또는 `google`) 로 바꾸고 §0 셀부터 다시 실행하면 됩니다.
> 노트북 코드는 한 줄도 고치지 않습니다(`utils.get_llm()` 이 공급자 차이를 흡수하고,
> `bootstrap.to_text()` 가 응답 형식/`<think>` 차이를 흡수). NVIDIA 모델은 §0-B 셀에서 개별 호출도 가능합니다.

## 4. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - **0. 환경 설정**: `utils.reload_env()` + `agentic_lib` import + 패키지 설치 + 연결 테스트
   - **0-B. NVIDIA build 직접 호출**: `get_llm('nvidia')` 로 기본 모델 개별 호출(키 없으면 안내만)
   - **1. Tool Use**: `@tool` / `bind_tools` / 자동 도구 루프 (`tool_list`, `tool_map`)
   - **2. Memory**: 메시지 히스토리 단기 기억 → LangGraph `MemorySaver` 장기 기억(thread_id)
   - **3. Planning**: `bind_tools([ExecutionPlan])` + `PydanticToolsParser`(스키마를 도구로 호출하는 구조화 출력) → `execute_plan` 으로 자동 실행
   - **4. Reasoning**: Chain of Thought, `create_react_agent`
   - **5. 통합 에이전트**: 4가지 역량 결합
3. 클라우드 API 라 모델 로딩 대기가 없습니다. OpenRouter(`openrouter/free`)로 전환하면 호출마다 응답 모델이 바뀔 수 있어 결과가 조금씩 달라집니다.

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` 미설정·오타, 또는 NVIDIA 크레딧 소진 |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경 |
| `tool_calls` 가 비어 있음 / 도구 호출 실패 | 도구 호출을 지원하지 않는 모델일 수 있음. 기본값 `nvidia` + `deepseek-ai/deepseek-v4.1-flash` 로 되돌려 비교 |
| 출력에 `<think>...</think>` / `[{'type':'text',...}]` 가 보임 | 노트북은 `bootstrap.to_text()` 로 자동 정규화. 직접 `print(resp.content)` 한 곳이 없는지 확인 |
| 구조화 출력(Planning) 오류 | `ChatNVIDIA.with_structured_output()` 은 `guided_json` 파라미터를 보내 deepseek 에서 `[400] unknown field` 가 납니다. 노트북은 이를 피하려고 도구 호출 방식(`bind_tools` + `PydanticToolsParser`)을 씁니다. `plan` 이 `None` 이면 셀을 다시 실행하세요. |

## 6. 명령 요약 (복붙용)

```bat
cd notebooks && copy .env.example .env
REM .env 에 NVIDIA_API_KEY 입력, LLM_PROVIDER=nvidia 확인 후 Jupyter 실행
uv run jupyter notebook
```
