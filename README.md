# Agentic AI 실습 (26-2) — M01 ~ M02

Agentic AI 강의 **M01 ~ M02** 실습용 노트북과 공통 코드, uv 환경 설정을 담은 폴더입니다.

- 실행 환경: **Windows 11 + CMD** · Python **3.11**(`uv` 관리)
- LLM: 무료 클라우드 API 두 가지를 사용합니다. 기본은 **NVIDIA build**(`deepseek-ai/deepseek-v4.1-flash`),
  비교 대상은 **OpenRouter**(`openrouter/free`)입니다. 로컬 GPU나 로컬 LLM 서버는 필요 없습니다.
- 노트북별 상세 설치·실행 방법은 [`notebooks/env_guides/`](notebooks/env_guides/README.md) 에 있습니다.

## 폴더 구성

```
practice_26-1\
├─ pyproject.toml, uv.lock, .python-version   uv 환경 설정(Python 3.11 고정)
└─ notebooks\
   ├─ M01_*.ipynb, M02_*.ipynb   실습 노트북
   ├─ utils.py                   LLM 공급자 선택(get_llm)·셸 실행(run_cmd) 등 공통 유틸
   ├─ agentic_lib\               노트북 공통 라이브러리(M01~M02 에서 쓰는 모듈)
   ├─ env_guides\                노트북별 환경 설치·실행 가이드
   └─ .env.example               LLM 설정 템플릿 → .env 로 복사해서 사용
```

## 환경 설치 (CMD, 이 폴더에서 실행)

```bat
REM 1) uv 설치 (1회 — uv 설치 스크립트만 PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

REM 2) 가상환경 생성 + 기본 의존성 설치
uv venv --python 3.11
uv sync

REM 3) Jupyter 설치 + 커널 등록
uv pip install jupyter ipykernel
uv run python -m ipykernel install --user --name=agentic-ai-venv --display-name "Agentic AI (uv)"

REM 4) LLM 설정 파일 만들기 (notebooks\ 에서 1회)
copy notebooks\.env.example notebooks\.env
REM    → notebooks\.env 를 열어 NVIDIA_API_KEY, OPENROUTER_API_KEY 를 입력

REM 5) Jupyter 실행 후 커널 "Agentic AI (uv)" 선택
uv run jupyter notebook notebooks/
```

노트북에 필요한 추가 패키지는 실행 중 `utils.uv_install()` 로 자동 설치됩니다.

## LLM API 키 발급과 `.env` 설정

| 공급자 | `LLM_PROVIDER` | 키 발급 | 기본 모델 | 비고 |
|---|---|---|---|---|
| **NVIDIA build** (기본) | `nvidia` | [build.nvidia.com](https://build.nvidia.com) → 모델 페이지 → `Get API Key` | `deepseek-ai/deepseek-v4.1-flash` | 무료 크레딧, 빠른 응답(1~2초), 병렬 도구 호출 지원 |
| **OpenRouter** (비교) | `openrouter` | [openrouter.ai](https://openrouter.ai) → `Keys` → `Create Key` | `openrouter/free` | 무료 모델 자동 선택 라우터, 하루 50요청(10크레딧 이상 충전 시 1,000요청) |

```ini
# notebooks\.env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

OpenRouter 로 전환하려면 `LLM_PROVIDER=openrouter` 한 줄만 바꾸면 됩니다. `utils.get_llm()` 이 공급자 차이를
처리하므로 노트북 코드는 고치지 않아도 됩니다. Google Gemini(`google`), Anthropic, OpenAI 는 선택 사항입니다.

## 주의

- venv 는 폴더를 옮기거나 이름을 바꾸면 깨집니다. 이동 후에는 `.venv` 를 지우고 2)~3) 단계를 다시 실행하세요.
- `notebooks\.env` 에는 API 키가 들어가므로 공유하지 마세요.
