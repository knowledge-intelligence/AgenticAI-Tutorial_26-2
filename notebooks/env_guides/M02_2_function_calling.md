# M02_2_function_calling.ipynb — 환경 설치·구축·실행 가이드

> 보충 노트북: **모델·공급자별 함수 호출(function calling) 신뢰도 4자 비교**. NVIDIA build 기본 모델과
> OpenRouter 무료 모델 세 가지를 같은 요청으로 N회(N=10) 반복 호출해, 도구 호출 성공 여부가
> **모델 크기**만이 아니라 **모델 특성**과 **공급자 가용성**에도 좌우된다는 점을 정량 비교합니다.
> `M02_3_mcp_a2a.ipynb` §7 에서 참조됩니다.

## 0. 전제

- Windows 11 + CMD + Python 3.11(uv). 공통 준비는 [README.md](README.md) 참고.
- 모두 클라우드 API 로 호출하므로 로컬 서버나 모델 다운로드가 필요 없습니다.

## 1. 필요한 것

| 구분 | 내용 |
|---|---|
| Python 패키지 | `langchain`, `langchain-openai`, `langchain-nvidia-ai-endpoints`, `openai` (환경 셀이 자동 설치) |
| 키 | `NVIDIA_API_KEY`(NVIDIA build), `OPENROUTER_API_KEY`(OpenRouter), 이 두 개만 있으면 됨 |

### 비교 대상

| # | 공급자 · 모델 | 보는 점 |
|---|---|---|
| ① | **NVIDIA build** · `deepseek-ai/deepseek-v4.1-flash` (기본) | 모델 고정으로 재현성이 높고, 빠르며, 병렬 도구 호출 지원 |
| ② | **OpenRouter** · `liquid/lfm-2.5-2.6b:free` (소형 2.6B) | 작은 모델도 규격에 맞는 `tool_calls` 를 만드는지 |
| ③ | **OpenRouter** · `nvidia/nemotron-3-super-120b-a12b:free` (대형) | 유효한 호출은 만들지만 한 응답에 도구를 하나만 부르는 경향이 있는지 |
| ④ | **OpenRouter** · `openrouter/free` (라우터) | 가용성은 높지만 호출마다 응답 모델이 바뀌는지 |

## 2. 설치 (CMD)

파이썬 패키지는 노트북이 `utils.uv_install([...])` 로 자동 설치합니다. 수동으로 설치하려면 아래처럼 실행합니다.

```bat
uv pip install langchain langchain-openai langchain-nvidia-ai-endpoints openai
```

## 3. `.env`

`notebooks/.env` 에 두 키만 있으면 됩니다. 비교 모델 ②~④ 는 노트북 코드에서 직접 지정하므로
`OPENROUTER_MODEL` 값과 무관하게 실행됩니다.

```ini
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=deepseek-ai/deepseek-v4.1-flash   # 실험 ① 에서 사용
OPENROUTER_API_KEY=sk-or-...
```

> OpenRouter 무료 모델은 하루 50요청으로 제한됩니다. 이 노트북은 실험 ②~④(각 10회)와 §8 측정으로
> OpenRouter 를 수십 번 호출하므로, 같은 날 여러 번 돌리면 한도(`429`)에 걸릴 수 있습니다.
> 분당 한도를 넘지 않도록 노트북은 OpenRouter 호출 사이에 `OR_PAUSE`(기본 3초) 간격을 두고, 429 는 자동 재시도(`max_retries=5`)합니다. 그래서 실행에 몇 분 걸립니다.

## 4. 실행 순서

1. 커널 `Agentic AI (uv)` 선택
2. 위에서부터 실행:
   - §0 환경 셀 → §1 비교 모델 & 모델 팩토리(`make_llm`) → §2 도구/분류기 셀(`TOOL_OK` / `MALFORMED` / `NO_TOOL` / `ERROR`)
   - §3 실험 ① NVIDIA `deepseek-v4.1-flash` ★기본
   - §4 실험 ② OpenRouter 소형 `lfm-2.5-2.6b` · §5 실험 ③ OpenRouter 대형 `nemotron-3-super-120b` (모델 크기 축)
   - §6 실험 ④ OpenRouter `openrouter/free` (공급자 가용성 축) → §6-1 실제 도구 실행 루프
   - §7 비교 결과(4자) → §8 멀티(병렬) function calling 측정(N=8) → §9 정리
3. NVIDIA build 는 `ChatNVIDIA`, OpenRouter 는 `ChatOpenAI(base_url="https://openrouter.ai/api/v1")` 로 접속합니다.
   OpenRouter 안에서 모델을 바꾸는 것은 `model` 문자열 한 줄뿐입니다.
4. 무료 모델 결과는 시간대·부하에 따라 달라지므로, 표의 수치는 실행할 때마다 직접 확인합니다.

## 5. 자주 겪는 문제

| 증상 | 원인/해결 |
|---|---|
| 실험 ②·③ 에 `ERROR` 가 많이 섞임 | 고정한 `:free` 모델의 과부하(`503 provider_overloaded`)나 요청 한도(`429`). 공급자 가용성 축이 보여 주려는 현상이며, 실제로 쓸 때는 `OPENROUTER_MODEL=openrouter/free` 권장 |
| 실험 ④ 응답 모델이 매번 다름 | `openrouter/free` 는 요청마다 가용한 무료 모델을 고르는 라우터라 정상 동작(재현성은 낮음) |
| 대형 모델이 두 도구 중 하나만 호출 | `nemotron-3-super-120b` 의 경향. 에이전트 루프를 여러 번 돌면 결국 처리하지만 왕복 횟수가 늘어남 |
| `410 Gone` (NVIDIA) | 모델이 서비스 종료됨. `NVIDIA_MODEL` 을 build.nvidia.com 에 현재 올라와 있는 모델(예: `deepseek-ai/deepseek-v4.1-flash`)로 변경 |
| `401 Unauthorized` | `.env` 의 `NVIDIA_API_KEY` / `OPENROUTER_API_KEY` 미설정·오타 |
| `<think>` 가 섞여 나옴 | 일부 모델은 사고 과정을 함께 출력함. 표시용은 `bootstrap.to_text()` 로 정리 |

## 6. 명령 요약 (복붙용)

```bat
REM .env 에 NVIDIA_API_KEY / OPENROUTER_API_KEY 확인
uv pip install langchain langchain-openai langchain-nvidia-ai-endpoints openai
REM 이후 노트북 셀을 위에서부터 실행(로컬 서버 불필요)
```
