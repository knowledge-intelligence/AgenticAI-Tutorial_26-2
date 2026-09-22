# M01_1_intro.ipynb — 환경 설치·구축·실행 가이드

> 0주차: 과목 소개 및 환경 설정. 이 노트북은 강의 전체에서 쓰는 **개발 환경**과
> **기본 LLM(NVIDIA build + `deepseek-ai/deepseek-v4.1-flash`)** 을 처음 구성합니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-google-genai`, `langchain-nvidia-ai-endpoints`, `langgraph`, `python-dotenv` (§6-B 셀이 필요 시 자동 설치) |
| 기본 LLM | **NVIDIA build** + **`deepseek-ai/deepseek-v4.1-flash`** (`NVIDIA_API_KEY` 필요, 무료 크레딧) |
| 비교 LLM | **OpenRouter** + **`openrouter/free`** (`OPENROUTER_API_KEY` 필요, 무료 모델) |
| (선택) 기타 클라우드 | `GOOGLE_API_KEY` (Gemini 무료 티어), Anthropic, OpenAI |

## 2. API 키 발급 (필수)

로컬 설치 없이 두 무료 클라우드 API 의 키만 발급하면 됩니다.

- **NVIDIA build**: [build.nvidia.com](https://build.nvidia.com) 로그인 → 모델 페이지 → `Get API Key` → `NVIDIA_API_KEY=nvapi-...`
- **OpenRouter**: [openrouter.ai](https://openrouter.ai) 로그인 → `Keys` → `Create Key` → `OPENROUTER_API_KEY=sk-or-...`
  (무료 모델은 하루 50요청, 크레딧 10 이상 충전 시 하루 1,000요청)

## 3. `.env` 설정

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
# OpenRouter 와 비교하려면 위 LLM_PROVIDER 를 openrouter 로 바꿈
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
# (선택) Google Gemini
GOOGLE_API_KEY=
```

> **공급자 전환**: `.env` 의 `LLM_PROVIDER` 만 `nvidia` ↔ `openrouter` (또는 `google`) 로 바꾸면 됩니다.
> 노트북 코드는 한 줄도 고치지 않습니다(`utils.get_llm()` 이 공급자 차이를 흡수).

## 4. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - 섹션 1~2: uv/패키지 점검
   - 섹션 3~6: 공급자 선택 → `get_llm()` 연결 테스트 (`NVIDIA_API_KEY` 가 있어야 함)
   - 섹션 6-B: 무료 클라우드 API(NVIDIA build·OpenRouter) 접속·테스트 (키가 있는 서비스만 호출하고, 없으면 안내만 출력)
   - 섹션 7~13: LLM vs Agent, 4대 역량(도구·메모리·계획·추론), ReAct
3. 클라우드 API 라 모델 로딩 대기가 없으며, NVIDIA `deepseek-v4.1-flash` 는 보통 1~2초 안에 응답합니다.

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` 미설정·오타, 또는 NVIDIA 크레딧 소진 |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경 |
| 출력에 `<think>...</think>` 가 보임 | 일부 모델은 사고 과정을 함께 출력함. 노트북은 `bootstrap.to_text()` 로 자동 제거 |
| 한글이 깨짐(`cp949`) | 노트북(Jupyter)은 UTF-8 이라 정상. 일반 CMD 출력만 영향 |

## 6. 명령 요약 (복붙용)

```bat
cd notebooks && copy .env.example .env
REM .env 에 NVIDIA_API_KEY / OPENROUTER_API_KEY 입력, LLM_PROVIDER=nvidia 확인 후 Jupyter 실행
uv run jupyter notebook
```
