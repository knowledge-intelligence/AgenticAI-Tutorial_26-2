# M02_3_mcp_a2a.ipynb — 환경 설치·구축·실행 가이드

> 모듈 1(2-4주차) **Part B**: **도구(Tools) · MCP · A2A**. LangChain 도구 정의,
> MCP(Model Context Protocol) 아키텍처, A2A(Agent-to-Agent) 3대 패턴(계층형/순차형/수평형),
> Individual Tool Agent 를 실습합니다. 로컬 LLM 서버 연결/서빙은 **Part A**
> (`M02_1_local_llm.ipynb`)에서 먼저 확인하세요.
> 기본 LLM 은 **로컬 Ollama + `qwen3:8b`**(네이티브 도구 호출 지원)입니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).
- 로컬 LLM 서버(Ollama/llama.cpp) 준비는 [M02_1_local_llm.md](M02_1_local_llm.md) 참고.
  이 노트북은 `.env` 의 `LLM_PROVIDER` 를 그대로 사용합니다(`utils.get_llm()`).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-community`, `langchain-google-genai`, `langchain-anthropic`, `openai`, `requests`, `ddgs` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 로컬 LLM | **Ollama** 서버 + **`qwen3:8b`** — §7/§8 에이전트의 네이티브 `tool_calls` 안정 |
| 웹 검색 도구 | **DuckDuckGo**(`ddgs`) — §4 도구 실습에서 **네트워크 필요** |
| (선택) 클라우드 비교/폴백 | `GOOGLE_API_KEY` (Gemini 무료 티어) |

## 2. 로컬 LLM 준비 (Ollama)

도구 호출 실습이므로 네이티브 `tool_calls` 가 안정적인 **Ollama + `qwen3:8b`** 를 권장합니다.

```bat
REM Ollama 설치·실행·모델 (Part A 에서 이미 했다면 생략)
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags
```

> llama.cpp 등 보조 서버 준비는 [M02_1_local_llm.md](M02_1_local_llm.md) 의 §3 참고.

## 3. 네트워크 의존성 (웹 검색 도구)

§4 도구 실습은 `langchain_community.tools.DuckDuckGoSearchRun`(패키지 `ddgs`)으로
**실제 웹 검색**을 수행합니다. 인터넷 연결이 필요합니다.

```bat
REM setup 셀이 자동 설치하지만, 수동 설치도 가능
uv pip install ddgs langchain-community
```

> **오프라인/사내망**에서 DuckDuckGo 가 막히면, 노트북 도구 목록에서 `search`(DuckDuckGo) 대신
> `tools.search_web`(시뮬레이션)로 대체할 수 있습니다.

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

# 클라우드(Gemini)와 비교/폴백하려면 아래 키를 채움
GOOGLE_API_KEY=
```

> **로컬 ↔ 클라우드 전환**: `.env` 의 `LLM_PROVIDER` 만 `ollama` ↔ `google` 로 바꾸면 됩니다.
> 로컬 도구 호출이 불안정한 공급자(`llamacpp`/`vllm`)를 쓸 때는 `LLM_PROVIDER` 를 도구 호출이
> 안정적인 공급자(예: `ollama`, `google`)로 바꿔 주면 됩니다.

## 5. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - setup(자기완결) → §4 LangChain 도구 → §5 MCP(Host/Client/Server) → §6 A2A 3대 패턴
   - §7 LangChain 에이전트(도구 호출) → §8 Individual Tool Agent 실습
3. 첫 LLM 호출 시 모델을 메모리에 올리느라 수십 초 걸릴 수 있습니다(이후 빠름).

## 6. 도구 호출(function calling) 관련

- **Ollama + `qwen3:8b`** 는 네이티브 `tool_calls` 가 안정적이라 §7/§8 에이전트가 그대로 동작합니다.
- 로컬 `llamacpp`/`vllm` 은 버전에 따라 도구 호출이 불안정할 수 있어, `.env` 의 `LLM_PROVIDER` 를
  도구 호출이 안정적인 공급자(예: `ollama`, `google`)로 바꿔 주면 됩니다.
- 모델 크기에 따른 도구 호출 신뢰도 3자 비교는 보충 노트북 `M02_2_function_calling.ipynb` 참고.

## 7. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `Connection refused (11434)` | Ollama 서버 미실행 → `ollama serve` (Part A 가이드 참고) |
| `model 'qwen3:8b' not found` | 모델 미설치 → `ollama pull qwen3:8b` |
| DuckDuckGo 검색 오류/타임아웃 | 네트워크 문제. 오프라인이면 `tools.search_web`(시뮬레이션)로 대체 가능 |
| 출력에 `<think>...</think>` 가 보임 | qwen3 는 사고 모델. 노트북은 `bootstrap.to_text()` 로 자동 제거 |
| 도구 호출이 안 됨(로컬 소형 모델) | 모델이 작아서임. `qwen3:8b` 사용 또는 `LLM_PROVIDER` 를 `google` 등 클라우드로 전환 |

## 8. 명령 요약 (복붙용)

```bat
REM Ollama (Part A 에서 준비했다면 생략)
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags

REM 웹 검색 도구 + .env 준비 후 Jupyter 실행
uv pip install ddgs langchain-community
cd notebooks && copy .env.example .env
REM .env 에서 LLM_PROVIDER=ollama 확인
uv run jupyter notebook
```
