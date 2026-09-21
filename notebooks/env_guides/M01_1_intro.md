# M01_1_intro.ipynb — 환경 설치·구축·실행 가이드

> 0주차: 과목 소개 및 환경 설정. 이 노트북은 강의 전체에서 쓰는 **개발 환경**과
> **기본 LLM(로컬 Ollama + qwen3:8b)** 을 처음 구성합니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-google-genai`, `langchain-nvidia-ai-endpoints`, `langgraph`, `python-dotenv` (§6-B 셀이 필요 시 자동 설치) |
| 로컬 LLM | **Ollama** 서버 + **`qwen3:8b`** 모델 |
| (선택) 클라우드 비교 | `GOOGLE_API_KEY` (Gemini 무료 티어) · `NVIDIA_API_KEY` (NVIDIA build 무료 크레딧) |

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

`notebooks/.env.example` 를 복사해 `notebooks/.env` 를 만들고 아래처럼 둡니다.

```bat
cd notebooks
copy .env.example .env
```

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
> 노트북 코드는 한 줄도 고치지 않습니다(`utils.get_llm()` 이 공급자 차이를 흡수).
>
> **NVIDIA API Key 발급(무료 크레딧)**: [build.nvidia.com](https://build.nvidia.com) 로그인 → 모델 페이지 → `Get API Key` → `NVIDIA_API_KEY=nvapi-...`

## 4. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - 섹션 1~2: uv/패키지 점검
   - 섹션 3~6: 공급자 선택 → `get_llm()` 연결 테스트 (Ollama 서버가 떠 있어야 함)
   - 섹션 6-B: 무료 클라우드 API(Google·NVIDIA) 접속·테스트 (키가 있는 서비스만 호출, 없으면 안내만)
   - 섹션 7~13: LLM vs Agent, 4대 역량(도구·메모리·계획·추론), ReAct
3. 첫 LLM 호출 시 Ollama 가 모델을 메모리에 올리느라 수십 초 걸릴 수 있습니다(이후 빠름).

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `Connection refused (11434)` | Ollama 서버 미실행 → `ollama serve` |
| `model 'qwen3:8b' not found` | 모델 미설치 → `ollama pull qwen3:8b` |
| 응답이 매우 느림 | 첫 호출은 모델 로딩 시간 포함. GPU 가 있으면 자동 사용 |
| 출력에 `<think>...</think>` 가 보임 | qwen3 는 사고 모델. 노트북은 `bootstrap.to_text()` 로 자동 제거 |
| 한글이 깨짐(`cp949`) | 노트북(Jupyter)은 UTF-8 이라 정상. 일반 CMD 출력만 영향 |

## 6. 명령 요약 (복붙용)

```bat
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
cd notebooks && copy .env.example .env
REM .env 에서 LLM_PROVIDER=ollama 확인 후 Jupyter 실행
uv run jupyter notebook
```
