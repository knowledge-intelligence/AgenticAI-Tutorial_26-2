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
- 로컬 LLM 서버(Ollama) 준비는 [M02_1_local_llm.md](M02_1_local_llm.md) 참고.
  이 노트북은 `.env` 의 `LLM_PROVIDER` 를 그대로 사용합니다(`utils.get_llm()`).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langgraph`, `langchain`, `langchain-openai` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 로컬 LLM | **Ollama** 서버 + **`qwen3:8b`** — 각 전문 노드의 응답 생성에 사용 |
| 네트워크 | 불필요(로컬 프로세스 내 그래프 실행). 모델 다운로드 이후 오프라인 동작 |
| (선택) 클라우드 비교 | `GOOGLE_API_KEY` (Gemini 무료 티어) |

> **A2A(`M02_5`) 와의 차이**: A2A 는 각 에이전트를 **독립 HTTP 서버**로 띄워 프로토콜로 연결하지만,
> LangGraph 는 **한 프로세스 안의 그래프**로 협업 흐름(분기·순환·병렬)을 선언합니다. `httpx`/`uvicorn`/`a2a-sdk`
> 같은 서버·프로토콜 의존성이 필요 없습니다.

## 2. 로컬 LLM 준비 (Ollama)

```bat
REM Ollama 설치·실행·모델 (다른 노트북에서 이미 했다면 생략)
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags
```

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
# notebooks/.env — 기본은 로컬 Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b

# 클라우드(Gemini)와 비교하려면 아래 키를 채움
GOOGLE_API_KEY=
```

> **로컬 ↔ 클라우드 전환**: `.env` 의 `LLM_PROVIDER` 만 `ollama` ↔ `google` 로 바꾸면 됩니다.

## 5. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - setup(자기완결) → §1 전문 에이전트 → §2 상태(State) → §3 Planner 노드
   - §4 노드/라우터 → §5 그래프 조립·시각화 → §6 실행(스트리밍) → §7 병렬(`Send`) → §8 마무리
3. 첫 LLM 호출 시 모델을 메모리에 올리느라 수십 초 걸릴 수 있습니다(이후 빠름).
4. `graph.stream()` 은 노드가 끝날 때마다 `{노드이름: 상태갱신}` 이벤트를 흘려, 실행 흐름을 그대로 관측합니다.

## 6. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `Connection refused (11434)` | Ollama 서버 미실행 → `ollama serve` |
| `model 'qwen3:8b' not found` | 모델 미설치 → `ollama pull qwen3:8b` |
| `Graph must have an entrypoint` | `add_edge(START, "planner")` 등 진입 엣지 누락. 본 노트북은 이미 반영 |
| 조건부 엣지 분기가 안 됨 | `route_map` 에 **모든 전문 노드 + writer** 를 넣어야 함. 본 노트북은 이미 반영 |
| 병렬(`Send`) 결과가 덮어써짐 | `results` 채널에 리듀서 `Annotated[list, operator.add]` 필요. §7 은 이미 반영 |
| 출력에 `<think>...</think>` | qwen3 는 사고 모델. `bootstrap.invoke_text()`/`to_text()` 가 자동 제거 |
| 분해 JSON 오류 | 소형 모델이 형식을 어길 수 있음. `planner_node` 의 **폴백 파서**로 안전 처리 |

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
REM Ollama (이미 준비했다면 생략)
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags

REM LangGraph 패키지 + .env 준비 후 Jupyter 실행
uv pip install langgraph langchain langchain-openai
cd notebooks && copy .env.example .env
REM .env 에서 LLM_PROVIDER=ollama 확인
uv run jupyter notebook
```
