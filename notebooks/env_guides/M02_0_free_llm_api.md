# M02_0_free_llm_api.ipynb — 환경 설치·구축·실행 가이드

> 무료 클라우드 LLM API 세 가지(**Google AI Studio(Gemini)**, **NVIDIA build**, **OpenRouter**)를
> 연결·테스트하는 노트북. 로컬 Ollama 대신 무료 클라우드를 잠깐 쓰고 싶을 때의 진입점입니다.
> OpenRouter 는 OpenAI 호환이라 **OpenRouter SDK(OpenAI SDK) 직접 호출**과 **LangChain 연결** 두 방법을 모두 다룹니다.

## 0. 전제
- Windows 11 + CMD + Python 3.11(uv). 공통 준비는 [README.md](README.md) 참고.
- 강의 기본 커널 **`Agentic AI (uv)`** 에서 실행(로컬 Ollama 커널과 동일).
- 두 서비스 키는 **선택**입니다 — 설정한 것만 실제로 호출되고, 없는 것은 안내만 출력됩니다.

## 1. 필요한 것
| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain-google-genai`, `langchain-nvidia-ai-endpoints`, `openai`, `langchain-openai`(노트북 첫 셀이 자동 설치) |
| 키(선택) | `GOOGLE_API_KEY`(Gemini), `NVIDIA_API_KEY`(NVIDIA build), `OPENROUTER_API_KEY`(OpenRouter) |

## 2. 키 발급 & `.env` 설정

`notebooks/.env` 에 아래 중 있는 것만 채웁니다(`.env.example` 복사 후 편집).

```ini
# Google AI Studio (무료 티어) — https://aistudio.google.com → Get API Key
GOOGLE_API_KEY=AIza...

# NVIDIA build (무료 크레딧) — https://build.nvidia.com → 모델 페이지 → Get API Key
NVIDIA_API_KEY=nvapi-...
# (선택) 기본 엔드포인트를 바꿀 때만
# NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# OpenRouter (무료 모델 라우터) — https://openrouter.ai → Keys → Create Key
OPENROUTER_API_KEY=sk-or-...
# (선택) 기본값. openrouter/free 는 무료 모델을 자동 선택하는 라우터
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# OPENROUTER_MODEL=openrouter/free
```

### 발급 절차
- **Google AI Studio**: [aistudio.google.com](https://aistudio.google.com) 로그인 → `Get API Key` → `Create API key` → 키 복사.
- **NVIDIA build**: [build.nvidia.com](https://build.nvidia.com) 로그인 → 사용할 모델(예: `meta/llama-3.1-8b-instruct`) 페이지 →
  `Get API Key`(무료 크레딧 제공) → `nvapi-...` 키 복사.
- **OpenRouter**: [openrouter.ai](https://openrouter.ai) 로그인 → `Keys` → `Create Key` → `sk-or-...` 키 복사.
  신규 사용자는 소액 무료 할당을 받으며, `openrouter/free` 로 무료 모델을 자동 선택해 테스트할 수 있습니다.
  무료 모델 한도는 **하루 50요청**(크레딧 10달러 이상 충전 시 **하루 1,000요청**).

## 3. 설치 (CMD, 수동 시)
```bat
uv pip install langchain-google-genai langchain-nvidia-ai-endpoints openai langchain-openai
```
> 노트북 첫 셀이 `utils.uv_install([...])` 로 자동 설치하므로 보통 불필요합니다.

## 4. 실행 순서
1. 커널 `Agentic AI (uv)` 선택
2. 위에서부터 실행:
   - §0 환경 설정(패키지 설치 + 키 상태 확인)
   - §1 Google Gemini 테스트(`utils.get_llm('google')`)
   - §2 NVIDIA build 테스트(`ChatNVIDIA`)
   - §3 OpenRouter 테스트 — A) OpenRouter SDK(OpenAI SDK), B) LangChain(`utils.get_llm('openrouter')`)
   - §4 스트리밍(Google·NVIDIA·OpenRouter 공통), §5 세 서비스 응답 비교

## 5. 자주 겪는 문제
| 증상 | 원인/해결 |
|---|---|
| `[401] Unauthorized` (NVIDIA) | 키 미설정/오타/크레딧 소진. `.env` 의 `NVIDIA_API_KEY` 확인 |
| NVIDIA `ReadTimeout` | 대형 모델(70b 등)은 느림. `NVIDIA_MODEL` 을 `meta/llama-3.1-8b-instruct` 등 작은 모델로 |
| `key set: False`인데 .env엔 있음 | 노트북은 CWD=`notebooks/` 라 자동 로드됨. 스크립트로 돌릴 땐 `notebooks/` 에서 실행 |
| Google 응답이 `[{...}]` | Gemini list content — `bootstrap.to_text()` 로 정규화(노트북이 처리) |
| `모델명 not found` (NVIDIA) | build.nvidia.com 각 모델 페이지에서 정확한 `provider/model` 이름 확인 |
| `429 Rate limit` (OpenRouter) | 무료 모델 한도 초과(하루 50요청). 잠시 후 재시도하거나 10크레딧 이상 충전(1000요청/일) |
| `401 No auth` (OpenRouter) | `OPENROUTER_API_KEY`(`sk-or-...`) 미설정/오타 확인 |

## 6. 명령 요약 (복붙용)
```bat
copy .env.example .env
REM .env 에 GOOGLE_API_KEY / NVIDIA_API_KEY / OPENROUTER_API_KEY 채우기
uv pip install langchain-google-genai langchain-nvidia-ai-endpoints openai langchain-openai
REM 이후 노트북 셀을 위에서부터 실행
```
