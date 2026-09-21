# M02_1_local_llm.ipynb — 환경 설치·구축·실행 가이드

> 모듈 1(2-4주차) **Part A**: 로컬 LLM **연결(Connectivity)**. 로컬 LLM 서버
> (**Ollama** 1순위 / **llama.cpp** 보조)를 **OpenAI 호환 API**(`/v1`)로 구동·연결하고
> 추론 동작을 확인합니다. 도구·MCP·A2A 는 Part B(`M02_3_mcp_a2a.ipynb`)에서 다룹니다.
> 기본 LLM 은 **로컬 Ollama + `qwen3:8b`**(네이티브 도구 호출 지원)입니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-community`, `langchain-google-genai`, `langchain-anthropic`, `openai`, `requests` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 로컬 LLM (1순위) | **Ollama** 서버 + **`qwen3:8b`** 모델 — 네이티브 `tool_calls` 안정 |
| 로컬 LLM (보조) | **llama.cpp**(`llama-cpp-python`) + GGUF 모델 — 프리빌트 휠(컴파일러 불필요) |
| (선택) 클라우드 비교/폴백 | `GOOGLE_API_KEY` (Gemini 무료 티어) |

## 2. 로컬 LLM 준비 — Ollama (1순위, 권장)

```bat
REM Ollama 설치 (1회)
winget install --id Ollama.Ollama -e

REM 서버 실행 (자동 실행 안 되면 수동으로)
ollama serve

REM 모델 다운로드 (약 5GB, 1회) — qwen3:8b 는 네이티브 도구 호출 지원
ollama pull qwen3:8b

REM 동작 확인 (OpenAI 호환 엔드포인트가 11434 포트에 떠 있는지)
curl.exe http://localhost:11434/api/tags
```

> 노트북은 `.env` 의 `LLM_PROVIDER` 를 그대로 사용합니다(`utils.get_llm()`). 서버/모델 준비 상태는
> 아래 **연결 테스트(`connection_test`) 셀**이 OpenAI 호환 `/v1/models` 로 확인합니다.

## 3. (보조) 로컬 LLM 준비 — llama.cpp + GGUF

Ollama 대신/추가로 llama.cpp 서버를 쓰고 싶을 때만 진행합니다. 노트북의 **모델/백엔드
확인 → 설치 → 다운로드 → 기동 → 헬스체크** 셀이 아래 과정을 자동화합니다.

```bat
REM (CPU) 사전 빌드 휠 — 컴파일러 불필요
uv pip install "llama-cpp-python[server]" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

REM (GPU, CUDA 12.4 휠) — 최신 CUDA 13 드라이버에서도 하위호환 동작
uv pip install --reinstall-package llama-cpp-python "llama-cpp-python[server]" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

REM GGUF 모델은 노트북의 '모델 다운로드' 셀이 huggingface_hub 로 받습니다(예: qwen2.5-0.5b / llama3.1-8b).

REM 서버 기동 (OpenAI 호환 /v1) — GPU 면 --n_gpu_layers -1, CPU 면 0
python -m llama_cpp.server --model <GGUF경로> --model_alias llamacpp --host 0.0.0.0 --port 8000 --n_gpu_layers -1 --n_ctx 4096

REM 엔드포인트 확인
curl.exe http://localhost:8000/v1/models
```

> **vLLM 은?** Linux/GPU 권장. Windows 는 Docker(WSL2) 백엔드 필요 + V2 Model Runner UVA
> 문제로 본 강의에서는 **사용하지 않습니다**(언급만).

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

# (보조) llama.cpp 사용 시
LLAMACPP_BASE_URL=http://localhost:8000/v1
LLAMACPP_MODEL=llamacpp

# 클라우드(Gemini)와 비교/폴백하려면 아래 키를 채움
GOOGLE_API_KEY=
```

> **로컬 ↔ 클라우드 전환**: `.env` 의 `LLM_PROVIDER` 만 `ollama` ↔ `google` 로 바꾸면 됩니다.
> 모든 로컬/클라우드 공급자는 OpenAI 호환 `/v1` 이라 `utils.get_llm()` 으로 동일하게 씁니다.

## 5. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - setup(자기완결) → Ollama 점검 → (보조) llama.cpp 서버 → 로컬 LLM 연결/추론 테스트
3. 첫 LLM 호출 시 모델을 메모리에 올리느라 수십 초 걸릴 수 있습니다(이후 빠름).
4. 도구·MCP·A2A 실습은 이어서 **Part B**(`M02_3_mcp_a2a.ipynb`)로 진행합니다.

## 6. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| `Connection refused (11434)` | Ollama 서버 미실행 → `ollama serve` |
| `model 'qwen3:8b' not found` | 모델 미설치 → `ollama pull qwen3:8b` |
| llama.cpp `Connection refused (8000)` | 서버 미기동 → 노트북 '기동' 셀 실행, `utils.tail_logs("llamacpp")` 로 로딩 확인 |
| 응답이 매우 느림 | 첫 호출은 모델 로딩 시간 포함. GPU 가 있으면 자동 사용 |
| 출력에 `<think>...</think>` 가 보임 | qwen3 는 사고 모델. 노트북은 `bootstrap.to_text()` 로 자동 제거 |

## 7. 명령 요약 (복붙용)

```bat
REM 1순위: Ollama
winget install --id Ollama.Ollama -e
ollama serve
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags

REM .env 준비 후 Jupyter 실행
cd notebooks && copy .env.example .env
REM .env 에서 LLM_PROVIDER=ollama 확인
uv run jupyter notebook
```
