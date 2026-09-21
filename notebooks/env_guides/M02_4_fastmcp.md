# M02_4_fastmcp.ipynb — 환경 설치·구축·실행 가이드

> FastMCP 로 **MCP Host · Client · Server** 를 구축해 간단한 도구 사용을 보여주는 노트북.
> 인메모리 전송을 써서 별도 프로세스/네트워크 없이 노트북 한 곳에서 전체 흐름을 실행합니다.

## 0. 전제
- Windows 11 + CMD + Python 3.11(uv). 공통 준비는 [README.md](README.md) 참고.
- 기본 LLM = 로컬 **Ollama + `qwen3:8b`**(Host 역할). `ollama serve` + `ollama pull qwen3:8b`.

## 1. 필요한 것
| 구분 | 내용 |
|---|---|
| Python 패키지 | `fastmcp`(노트북 첫 셀 `utils.uv_install(['fastmcp'])` 로 자동 설치), `langchain-openai` |
| 로컬 LLM | Ollama(`:11434`) + `qwen3:8b` (도구 선택용 Host) |

## 2. 설치 (CMD)
```bat
REM FastMCP 설치(수동 설치 시). 노트북이 자동 설치하므로 보통 불필요
uv pip install fastmcp

REM 로컬 LLM 준비(공통)
ollama serve
ollama pull qwen3:8b
curl.exe http://localhost:11434/api/tags
```

## 3. `.env`
기본값(로컬 Ollama)이면 그대로 두면 됩니다.
```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
```

## 4. 실행 순서
1. 커널 `Agentic AI (uv)` 선택
2. 위에서부터 실행:
   - §0 환경 설정(fastmcp 설치 + LLM 준비)
   - §1 **Server**: `FastMCP` + `@mcp.tool` 도구 정의
   - §2 **Client**: `Client(mcp)` 인메모리 연결 → `list_tools` / `call_tool` (셀 최상위 `await`)
   - §3 **Host**: Ollama LLM 이 도구를 선택 → Client 로 실행 → 최종 답변
3. §2·§3 은 `async` API 라 셀에서 `await` 를 직접 사용합니다(Jupyter 최상위 await 지원).

## 5. 자주 겪는 문제
| 증상 | 원인/해결 |
|---|---|
| `ModuleNotFoundError: fastmcp` | 첫 셀 `utils.uv_install(['fastmcp'])` 실행, 또는 `uv pip install fastmcp` |
| `RuntimeError: no running event loop` / await 오류 | 반드시 Jupyter 커널에서 실행(최상위 await 지원). 순수 스크립트면 `asyncio.run(...)` 필요 |
| Host 가 도구를 안 부름 | Ollama `qwen3:8b` 사용 확인(소형 모델은 완성도 낮을 수 있음). `ollama list` 로 모델 점검 |
| `<think>` 노출 | 프롬프트에 `/no_think`, 출력은 `bootstrap.to_text()` 로 정리 |

## 6. 명령 요약 (복붙용)
```bat
uv pip install fastmcp
ollama serve
ollama pull qwen3:8b
REM 이후 노트북 셀을 위에서부터 실행
```
