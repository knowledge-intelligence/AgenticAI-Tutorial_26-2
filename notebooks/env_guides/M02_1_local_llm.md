# M02_1_local_llm.ipynb — 환경 설치·구축·실행 가이드

> 모듈 1(2-4주차) **Part A**: **OpenAI 호환 LLM API 연결(Connectivity)**. 무료 클라우드 LLM 두 곳
> (**경로 1: NVIDIA build** / **경로 2: OpenRouter**)을 **OpenAI 호환 API**(`/v1`)로 연결하고 응답을 확인합니다.
> 두 서비스 모두 같은 `ChatOpenAI` 코드에 `base_url`·키·모델만 바꿔 접속합니다.
> 도구·MCP·A2A 는 Part B(`M02_3_mcp_a2a.ipynb`)에서 다룹니다.
> 파일 이름은 이전 과정과 같지만, 로컬 서버 설치나 모델 다운로드는 필요 없습니다.

## 0. 전제

- Windows 11 + **CMD(`cmd.exe`)** + Python **3.11**(`uv` 관리)
- 공통 1회 준비는 [README.md](README.md) 를 먼저 따라 하세요(uv 설치 → `uv venv` → `uv sync` → 커널 등록).
- 키 발급 절차는 [M02_0_free_llm_api.md](M02_0_free_llm_api.md) 를 참고하세요.

## 1. 이 노트북이 필요로 하는 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-nvidia-ai-endpoints`, `openai`, `requests` (setup 셀이 `utils.uv_install()` 로 자동 설치) |
| 경로 1 | **NVIDIA build** · `https://integrate.api.nvidia.com/v1` · `deepseek-ai/deepseek-v4.1-flash` (`NVIDIA_API_KEY` 필요) |
| 경로 2 | **OpenRouter** · `https://openrouter.ai/api/v1` · `openrouter/free` (`OPENROUTER_API_KEY` 필요) |

> 이 노트북은 `.env` 의 `LLM_PROVIDER` 값과 **무관하게** 두 경로를 각각 명시적으로 실행합니다.
> 경로별 키·모델·엔드포인트는 `.env` 의 `NVIDIA_*` / `OPENROUTER_*` 값을 쓰며, 모델과 엔드포인트를 따로
> 지정하지 않으면 위 표의 기본값이 적용됩니다.

## 2. 각 경로에서 하는 일

| 단계 | 내용 |
|---|---|
| (1) 연결 테스트 | `GET {base_url}/models` 를 `Authorization: Bearer <키>` 로 호출해 접속·인증을 확인하고, 설정한 모델이 목록에 있는지 점검 |
| (2) 응답 테스트 | `ChatOpenAI(base_url=..., api_key=..., model=...)` 로 같은 질문을 보내 OpenAI 호환 응답을 확인 |

두 경로의 코드는 동일하며 `base_url`·키·모델만 다릅니다. 이것이 **OpenAI 호환 프로토콜**의 핵심 이점입니다.
다른 노트북에서는 `utils.get_llm()` 이 NVIDIA 전용 커넥터 `ChatNVIDIA` 를 돌려주지만, 인터페이스(`.invoke()`)는 같습니다.

CMD 에서 연결 테스트를 직접 해 보려면 아래처럼 호출합니다(키는 본인 값으로 바꿈).

```bat
curl.exe -H "Authorization: Bearer nvapi-..." https://integrate.api.nvidia.com/v1/models
curl.exe -H "Authorization: Bearer sk-or-..." https://openrouter.ai/api/v1/models
```

## 3. `.env` 설정

`notebooks/.env.example` 를 복사해 `notebooks/.env` 를 만들고 아래처럼 둡니다.

```bat
cd notebooks
copy .env.example .env
```

```ini
# notebooks/.env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openrouter/free
```

> **공급자 전환**: 다른 노트북에서는 `.env` 의 `LLM_PROVIDER` 만 `nvidia` ↔ `openrouter` 로 바꾸면 됩니다.
> 두 공급자 모두 OpenAI 호환 `/v1` 이라 `utils.get_llm()` 으로 동일하게 씁니다.

## 4. 실행 순서

1. Jupyter 에서 커널을 **`Agentic AI (uv)`** 로 선택
2. 위에서부터 순서대로 셀 실행
   - setup(자기완결) → §1 공통 헬퍼(`connection_test`, `response_test`)
   - §2 경로 1: NVIDIA build 연결 테스트 → 응답 테스트
   - §3 경로 2: OpenRouter 연결 테스트 → 응답 테스트(`응답 모델` 출력으로 라우터가 고른 모델 확인)
   - §4 정리: 두 경로의 연결 상태와 설정 모델 제공 여부를 나란히 확인
3. 도구·MCP·A2A 실습은 이어서 **Part B**(`M02_3_mcp_a2a.ipynb`)로 진행합니다.

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| 연결 테스트 `401` | 키 미설정·오타. `.env` 의 `NVIDIA_API_KEY`(`nvapi-...`) / `OPENROUTER_API_KEY`(`sk-or-...`) 확인 후 setup 셀 재실행 |
| 연결은 되는데 `설정 모델 없음` 경고 | `NVIDIA_MODEL` / `OPENROUTER_MODEL` 이름 오타이거나 서비스에서 내려간 모델. 모델 페이지에서 정확한 이름 확인 |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| OpenRouter `503 provider_overloaded` / `429` | 고정한 `:free` 모델이 과부하이거나 요청 한도 초과. `OPENROUTER_MODEL=openrouter/free` 로 변경하고, 하루 한도(50요청)를 넘었으면 다음 날 재시도 |
| OpenRouter 응답 모델이 매번 다름 | `openrouter/free` 는 요청마다 가용한 무료 모델을 고르는 라우터라 정상 동작 |
| 출력에 `<think>...</think>` 가 보임 | 일부 모델은 사고 과정을 함께 출력함. 노트북은 `bootstrap.to_text()` 로 자동 제거 |

## 6. 명령 요약 (복붙용)

```bat
REM .env 준비 (NVIDIA_API_KEY, OPENROUTER_API_KEY 입력)
cd notebooks && copy .env.example .env

REM (선택) CMD 에서 두 엔드포인트 연결 확인
curl.exe -H "Authorization: Bearer nvapi-..." https://integrate.api.nvidia.com/v1/models
curl.exe -H "Authorization: Bearer sk-or-..." https://openrouter.ai/api/v1/models

REM Jupyter 실행
uv run jupyter notebook
```
