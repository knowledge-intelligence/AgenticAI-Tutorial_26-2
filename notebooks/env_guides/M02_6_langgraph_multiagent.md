# M02_6_langgraph_multiagent.ipynb — 환경 설치·구축·실행 가이드

> 모듈 1(2-4주차) **보충**: **LangGraph 멀티 에이전트(Supervisor 패턴)**. [`M02_5_a2a_multiagent.ipynb`](../M02_5_a2a_multiagent.ipynb)
> 와 **같은 실습**(계산·요약·작문 전문 에이전트 + 코디네이터)을, 표준 프로토콜 `a2a-sdk` 대신 **LangGraph**
> `StateGraph` 로 다시 구현합니다. 각 전문 에이전트는 **HTTP 서버가 아니라 그래프의 노드**이고, 위임은
> **조건부 엣지**로, 병렬 위임은 **`Send` 팬아웃**으로 표현합니다.
> 개념 소개는 [`M02_3_mcp_a2a.ipynb`](../M02_3_mcp_a2a.ipynb) 의 A2A 3패턴을 참고하세요.
> LLM 은 `.env` 의 **`LLM_PROVIDER`**(`utils.get_llm()`)로 결정되며, 각 노드(에이전트)의 두뇌로 사용합니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).
- API 키 준비와 연결 확인은 [M02_1_local_llm.md](M02_1_local_llm.md) 참고.
  이 노트북은 `.env` 의 `LLM_PROVIDER` 를 그대로 사용합니다(`utils.get_llm()`, 기본 `nvidia`).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langgraph`, `langchain`, `langchain-openai` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 기본 LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): 각 전문 노드의 응답 생성에 사용 |
| 네트워크 | 그래프는 한 프로세스 안에서 실행되지만, LLM 호출에는 인터넷 연결 필요 |
| (선택) 비교 | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini 무료 티어) |

> **A2A(`M02_5`) 와의 차이**: A2A 는 각 에이전트를 **독립 HTTP 서버**로 띄워 프로토콜로 연결하지만,
> LangGraph 는 **한 프로세스 안의 그래프**로 협업 흐름(분기·순환·병렬)을 선언합니다. `httpx`/`uvicorn`/`a2a-sdk`
> 같은 서버·프로토콜 의존성이 필요 없습니다.

## 2. LLM 준비 (NVIDIA build)

별도 설치 없이 `.env` 에 `NVIDIA_API_KEY` 만 있으면 됩니다. 키가 없다면
[build.nvidia.com](https://build.nvidia.com) 에서 발급하세요(다른 노트북에서 했다면 생략).

## 3. LangGraph 패키지 설치

setup 셀이 자동 설치하지만, 수동 설치도 가능합니다.

```bat
uv pip install langgraph langchain langchain-openai
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
   - setup(자기완결) → §1 전문 에이전트 → §2 상태(State) → §3 Planner 노드
   - §4 노드/라우터 → §5 그래프 조립·시각화 → §6 실행(스트리밍) → §7 병렬(`Send`) → §8 마무리
3. 노드마다 클라우드 LLM 을 호출하므로 그래프 실행은 네트워크 상태에 따라 수 초에서 수십 초 걸릴 수 있습니다.
4. `graph.stream()` 은 노드가 끝날 때마다 `{노드이름: 상태갱신}` 이벤트를 흘려, 실행 흐름을 그대로 관측합니다.

## 6. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` 미설정·오타 |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경 |
| `Graph must have an entrypoint` | `add_edge(START, "planner")` 등 진입 엣지 누락. 본 노트북은 이미 반영 |
| 조건부 엣지 분기가 안 됨 | `route_map` 에 **모든 전문 노드 + writer** 를 넣어야 함. 본 노트북은 이미 반영 |
| 병렬(`Send`) 결과가 덮어써짐 | `results` 채널에 리듀서 `Annotated[list, operator.add]` 필요. §7 은 이미 반영 |
| 출력에 `<think>...</think>` | 일부 모델은 사고 과정을 함께 출력함. `bootstrap.invoke_text()`/`to_text()` 가 자동 제거 |
| 분해 JSON 오류 | 모델이 형식을 어길 수 있음(특히 `openrouter/free` 로 전환 시). `planner_node` 의 **폴백 파서**로 안전 처리 |

## 7. LangGraph 핵심 심볼 (참고)

| 심볼 | 위치 | 역할 |
|---|---|---|
| `StateGraph` | `langgraph.graph` | 상태 기반 그래프 빌더 |
| `START` / `END` | `langgraph.graph` | 진입/종료 노드 상수 |
| `add_node` / `add_edge` | `StateGraph` | 노드 등록 / 고정 엣지 |
| `add_conditional_edges(src, router, map)` | `StateGraph` | 조건부 라우팅(분기·순환) |
| `compile()` → `.get_graph().draw_mermaid()` | `StateGraph` | 실행 그래프 컴파일 / 시각화 |
| `.stream(state)` / `.invoke(state)` | 컴파일된 그래프 | 스트리밍 관측 / 일괄 실행 |
| `Send(node, payload)` | `langgraph.types` | 팬아웃(병렬 위임) |
| `Annotated[list, operator.add]` | `typing` | 병렬 결과 팬인(리듀서) |

## 8. 명령 요약 (복붙용)

```bat
REM LangGraph 패키지 + .env 준비 후 Jupyter 실행
uv pip install langgraph langchain langchain-openai
cd notebooks && copy .env.example .env
REM .env 에 NVIDIA_API_KEY 입력, LLM_PROVIDER=nvidia 확인
uv run jupyter notebook
```
