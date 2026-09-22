# M02_3_mcp_a2a.ipynb — 환경 설치·구축·실행 가이드

> 모듈 1(2-4주차) **Part B**: **도구(Tools) · MCP · A2A**. LangChain 도구 정의,
> MCP(Model Context Protocol) 아키텍처, A2A(Agent-to-Agent) 3대 패턴(계층형/순차형/수평형),
> Individual Tool Agent 를 실습합니다. OpenAI 호환 LLM API 연결은 **Part A**
> (`M02_1_local_llm.ipynb`)에서 먼저 확인하세요.
> 기본 LLM 은 **NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`**(네이티브·병렬 도구 호출 지원)입니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).
- API 키 준비와 연결 확인은 [M02_1_local_llm.md](M02_1_local_llm.md) 참고.
  이 노트북은 `.env` 의 `LLM_PROVIDER` 를 그대로 사용합니다(`utils.get_llm()`, 기본 `nvidia`).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-community`, `langchain-google-genai`, `langchain-anthropic`, `openai`, `requests`, `ddgs` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 기본 LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY`): §7/§8 에이전트의 네이티브 `tool_calls` 안정 |
| 웹 검색 도구 | **DuckDuckGo**(`ddgs`) — §4 도구 실습에서 **네트워크 필요** |
| (선택) 비교 | **OpenRouter** + `openrouter/free` (`OPENROUTER_API_KEY`) · `GOOGLE_API_KEY` (Gemini 무료 티어) |

## 2. LLM 준비 (NVIDIA build)

도구 호출 실습이므로 네이티브 `tool_calls` 가 안정적이고 한 응답에서 여러 도구를 병렬로 부를 수 있는
**NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`** 를 기본으로 씁니다. 별도 설치 없이 `NVIDIA_API_KEY` 만
있으면 됩니다. 키가 없다면 [build.nvidia.com](https://build.nvidia.com) 에서 발급하세요(Part A 에서 했다면 생략).

## 3. 네트워크 의존성 (웹 검색 도구)

§4 도구 실습은 `langchain_community.tools.DuckDuckGoSearchRun`(패키지 `ddgs`)으로
**실제 웹 검색**을 수행합니다. 인터넷 연결이 필요합니다.

```bat
REM setup 셀이 자동 설치하지만, 수동 설치도 가능
uv pip install ddgs langchain-community
```

> **사내망 등**에서 DuckDuckGo 가 막히면, 노트북 도구 목록에서 `search`(DuckDuckGo) 대신
> `tools.search_web`(시뮬레이션)로 대체할 수 있습니다.

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
> 노트북 코드는 고치지 않습니다.

## 5. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - setup(자기완결) → §4 LangChain 도구 → §5 MCP(Host/Client/Server) → §6 A2A 3대 패턴
   - §7 LangChain 에이전트(도구 호출) → §8 Individual Tool Agent 실습
3. 클라우드 API 라 모델 로딩 대기가 없습니다.

## 6. 도구 호출(function calling) 관련

- **NVIDIA build + `deepseek-v4.1-flash`** 는 네이티브 `tool_calls` 가 안정적이고 병렬 도구 호출도 지원해 §7/§8 에이전트가 그대로 동작합니다.
- OpenRouter `openrouter/free` 로 전환하면 호출마다 응답 모델이 바뀌어, 도구 호출 결과가 실행할 때마다 달라질 수 있습니다.
  결과가 불안정하면 `LLM_PROVIDER=nvidia` 로 되돌리세요.
- 모델·공급자별 도구 호출 신뢰도 4자 비교는 보충 노트북 `M02_2_function_calling.ipynb` 참고.

## 7. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` 미설정·오타 (Part A 가이드 참고) |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경 |
| DuckDuckGo 검색 오류/타임아웃 | 네트워크 문제. 막혀 있으면 `tools.search_web`(시뮬레이션)로 대체 가능 |
| 출력에 `<think>...</think>` 가 보임 | 일부 모델은 사고 과정을 함께 출력함. 노트북은 `bootstrap.to_text()` 로 자동 제거 |
| 도구 호출이 안 됨 | 도구 호출을 잘 못하는 모델로 전환된 경우. `LLM_PROVIDER=nvidia` + `deepseek-ai/deepseek-v4.1-flash` 로 되돌림 |

## 8. 명령 요약 (복붙용)

```bat
REM 웹 검색 도구 + .env 준비 후 Jupyter 실행
uv pip install ddgs langchain-community
cd notebooks && copy .env.example .env
REM .env 에 NVIDIA_API_KEY 입력, LLM_PROVIDER=nvidia 확인
uv run jupyter notebook
```
