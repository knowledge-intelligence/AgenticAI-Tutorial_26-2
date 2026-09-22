# M02_5_a2a_multiagent.ipynb — 환경 설치·구축·실행 가이드

> 모듈 1(2-4주차) **보충**: **A2A 프로토콜 멀티 에이전트**. 표준 구현체 **`a2a-sdk`(a2a-python) 1.1.0**
> 으로 전문 에이전트(계산·요약·작문)를 실제 **A2A HTTP 서버**로 띄우고, **코디네이터**가 복합 요청을
> 분해해 각 에이전트에 **A2A 메시지로 위임**한 뒤 결과를 취합합니다.
> 개념 소개는 먼저 [`M02_3_mcp_a2a.ipynb`](../M02_3_mcp_a2a.ipynb) 의 A2A 3패턴을 참고하세요.
> 기본 LLM 은 **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`** 이며, 각 에이전트의 두뇌로 사용합니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).
- API 키 준비와 연결 확인은 [M02_1_local_llm.md](M02_1_local_llm.md) 참고.
  이 노트북은 `.env` 의 `LLM_PROVIDER` 를 그대로 사용합니다(`utils.get_llm()`, 기본 `nvidia`).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `a2a-sdk`(1.1.0), `uvicorn`, `httpx`, `langchain`, `langchain-openai` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 기본 LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): 각 전문 에이전트의 응답 생성에 사용 |
| 네트워크 | A2A 서버·클라이언트는 **로컬 루프백**(127.0.0.1)으로 통신. LLM 호출에는 인터넷 연결 필요 |
| (선택) 비교 | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini 무료 티어) |

> `a2a-sdk` 는 **프로토콜 버퍼 기반 타입**(`AgentCard`, `Message`, `Task` 등)과
> **서버(AgentExecutor/DefaultRequestHandler)·클라이언트(ClientFactory/A2ACardResolver)** API 를 제공합니다.
> 버전마다 API 가 크게 다르므로 본 노트북은 **1.1.0** 기준으로 작성되었습니다.

## 2. LLM 준비 (NVIDIA build)

별도 설치 없이 `.env` 에 `NVIDIA_API_KEY` 만 있으면 됩니다. 키가 없다면
[build.nvidia.com](https://build.nvidia.com) 에서 발급하세요(다른 노트북에서 했다면 생략).

## 3. A2A 패키지 설치

setup 셀이 자동 설치하지만, 수동 설치도 가능합니다.

```bat
uv pip install a2a-sdk uvicorn httpx
```

## 4. `.env` 설정

`notebooks/.env.example` 를 복사해 `notebooks/.env` 를 만들고 아래처럼 둡니다.

```bat
cd notebooks
copy .env.example .env
```

```ini
# notebooks/.env (기본은 NVIDIA build)
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash

# OpenRouter 와 비교하려면 LLM_PROVIDER=openrouter 로 바꿈
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

> **공급자 전환**: `.env` 의 `LLM_PROVIDER` 만 `nvidia` ↔ `openrouter` (또는 `google`) 로 바꾸면 됩니다.

## 5. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - setup(자기완결) → §1 임포트/헬퍼 → §2 AgentCard 정의 → §3 A2A 서버 기동
   - §4 카드 발견 → §5 단일 에이전트 호출 → §6 코디네이터(분해→위임→취합) → §7 정리(서버 종료)
3. 각 에이전트 서버는 **백그라운드 스레드**로 뜨며, 임의의 빈 포트를 자동 선택합니다(포트 충돌 방지).
4. 에이전트마다 클라우드 LLM 을 호출하므로 코디네이터 실행은 네트워크 상태에 따라 수 초에서 수십 초 걸릴 수 있습니다.
5. 노트북은 **비동기 A2A API** 를 최상위 `await` 로 호출합니다(Jupyter/ipykernel 지원).

## 6. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` 미설정·오타 |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경 |
| 서버 셀에서 `started=False` | 포트 준비 지연. 셀을 다시 실행하거나 잠시 후 재시도 |
| `Agent should enqueue Task before ...` | 실행기가 Task 를 먼저 큐에 넣지 않은 경우. 본 노트북 `LLMAgentExecutor` 는 `new_task` 를 먼저 enqueue 해 이를 방지 |
| 응답이 비어 있음 | 결과를 **Artifact** 로 첨부해야 함(`updater.add_artifact`). 본 노트북은 이미 반영 |
| 출력에 `<think>...</think>` | 일부 모델은 사고 과정을 함께 출력함. `bootstrap.invoke_text()`/`to_text()` 가 자동 제거 |
| 코디네이터 분해 JSON 오류 | 모델이 형식을 어길 수 있음(특히 `openrouter/free` 로 전환 시). 본 노트북은 **폴백 파서**로 안전 처리 |
| `RuntimeError: event loop ...` | 커널 재시작 후 위에서부터 순서대로 재실행(서버·클라이언트를 같은 루프에서 생성) |

## 7. A2A SDK 1.1.0 핵심 심볼 (참고)

| 심볼 | 위치 | 역할 |
|---|---|---|
| `AgentCard`/`AgentSkill`/`AgentCapabilities`/`AgentInterface` | `a2a.types` | 에이전트 명세(발견) |
| `Message`/`Part`/`Role`/`Task`/`TaskState` | `a2a.types` | 프로토콜 메시지·작업 타입 |
| `AgentExecutor`/`RequestContext` | `a2a.server.agent_execution` | 서버 측 실행 모델 |
| `EventQueue` | `a2a.server.events` | 결과 이벤트 큐 |
| `TaskUpdater` | `a2a.server.tasks.task_updater` | 작업 상태·Artifact 기록 |
| `DefaultRequestHandler` | `a2a.server.request_handlers` | 요청 처리기 |
| `InMemoryTaskStore` | `a2a.server.tasks` | 작업 저장소(데모) |
| `create_agent_card_routes`/`create_jsonrpc_routes` | `a2a.server.routes` | Starlette 라우트 |
| `ClientFactory`/`ClientConfig`/`A2ACardResolver` | `a2a.client` | 클라이언트 생성·카드 발견 |
| `TransportProtocol` | `a2a.utils` | 전송 바인딩(JSONRPC/GRPC/HTTP_JSON) |
| `new_text_message`/`new_text_part`/`new_task`/`get_stream_response_text` | `a2a.helpers.proto_helpers` | 메시지·작업 생성/파싱 |

## 8. 명령 요약 (복붙용)

```bat
REM A2A 패키지 + .env 준비 후 Jupyter 실행
uv pip install a2a-sdk uvicorn httpx
cd notebooks && copy .env.example .env
REM .env 에 NVIDIA_API_KEY 입력, LLM_PROVIDER=nvidia 확인
uv run jupyter notebook
```
