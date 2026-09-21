# M02_2_function_calling.ipynb — 환경 설치·구축·실행 가이드

> 보충 노트북: **함수 호출(function calling) 신뢰도 3자 비교** — 로컬 소형(`qwen2.5:0.5b`)
> vs 로컬 대형(`qwen3:8b`) vs 클라우드(`google`). "도구 호출 실패는 *로컬이라서*가 아니라
> *모델이 작아서*"임을 N회 반복 실험으로 보여줍니다. 모듈1(§7)에서 참조됩니다.

> 이 노트북은 본 강의의 기본 LLM 인 **Ollama** 를 그대로 사용합니다. 같은 Ollama 서버에서
> **모델 태그만 바꿔**(`qwen2.5:0.5b` ↔ `qwen3:8b`) 비교하므로, 별도 GGUF 다운로드나
> llama.cpp 서버 기동이 필요 없습니다.

## 0. 전제

- Windows 11 + CMD + Python 3.11(uv). 공통 준비는 [README.md](README.md) 참고.
- Ollama 서버(`ollama serve`)가 떠 있어야 합니다. GPU 가 있으면 `qwen3:8b` 가 자동으로 GPU 를 사용합니다.

## 1. 필요한 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-google-genai`(클라우드 비교), `openai` |
| 로컬 서버 | **Ollama** (OpenAI 호환 `:11434/v1`) — 이미 설치·기동되어 있으면 추가 작업 없음 |
| 모델 | 소형 `qwen2.5:0.5b`(~0.4GB), 대형 `qwen3:8b`(~5GB) — `ollama pull` 로 준비 |
| (선택) 클라우드 비교 | `GOOGLE_API_KEY` (또는 다른 클라우드 공급자) |

## 2. 설치 (CMD)

Ollama 설치·기동은 [README.md](README.md) / [M01_1_intro.md](M01_1_intro.md) 와 동일합니다.
이 노트북용으로 **두 모델**을 받아 둡니다(최초 1회).

```bat
REM Ollama 설치(1회) — 이미 설치되어 있으면 생략
winget install --id Ollama.Ollama -e

REM 서버 실행(자동 실행 안 되면 수동)
ollama serve

REM 두 로컬 모델 다운로드(최초 1회, 이후 캐시)
ollama pull qwen2.5:0.5b
ollama pull qwen3:8b

REM 동작 확인
curl.exe http://localhost:11434/api/tags
```

> 파이썬 패키지는 노트북이 `utils.uv_install([...])` 로 자동 설치합니다. 수동 설치 시:
> `uv pip install langchain langchain-openai langchain-google-genai openai`

## 3. `.env`

`notebooks/.env` 는 기본값(로컬 Ollama)이면 그대로 두면 됩니다. 클라우드 비교(실험 ③)는
`GOOGLE_API_KEY` 가 있을 때만 수행됩니다.

```ini
# 로컬 Ollama (기본)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
# 클라우드 비교 대상(예: Google). 없으면 실험 ③ 를 건너뜀
GOOGLE_API_KEY=AIzaSy...
```

## 4. 실행 순서

1. 커널 `Agentic AI (uv)` 선택
2. 위에서부터 실행:
   - 환경 셀 → 모델 팩토리 셀(`make_llm`, Ollama 서버/모델 사전 점검) → 도구/분류기 셀
   - 실험① `qwen2.5:0.5b` (Ollama 가 유효 `tool_calls` 는 생성하나, 다중 도구 요청의 완성도는 낮을 수 있음)
   - 실험② `qwen3:8b` (유효 `tool_calls` + 두 도구 모두 안정 호출 ~100%) ★핵심
   - 실험③ 클라우드 `google` (~100%)
   - 비교 결과(막대그래프) → 정리
3. 세 실험 모두 동일한 `ChatOpenAI(...).bind_tools(TOOLS)` 인터페이스를 쓰며, 로컬 모델 전환은
   `make_llm(model)` 의 `model` 문자열 한 줄뿐입니다. 서버 기동/종료 셀이 없습니다.

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| Ollama 서버 연결 실패 | CMD 에서 `ollama serve` 로 서버를 먼저 실행 |
| 모델 없음 경고 | `ollama pull qwen2.5:0.5b` / `ollama pull qwen3:8b` 로 받기 |
| 소형 모델 완성도 낮음 | Ollama 는 유효 `tool_calls` 를 만들지만, 소형 모델은 다중 도구 요청에서 일부를 빠뜨릴 수 있음(정상) |
| 실험③ 건너뜀 | `.env` 에 `GOOGLE_API_KEY`(또는 다른 클라우드 키) 미설정 |
| `<think>` 가 섞여 나옴 | 프롬프트에 `/no_think`. 표시용은 `bootstrap.to_text()` 로 정리 |

## 6. 명령 요약 (복붙용)

```bat
ollama pull qwen2.5:0.5b
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags
uv pip install langchain langchain-openai langchain-google-genai openai
REM 이후 노트북 셀을 위에서부터 실행(서버 기동/종료 불필요)
```
