"""
Agentic AI Tutorial - 공통 유틸리티 모듈
모든 노트북에서 공통으로 사용하는 함수/변수를 여기에 정의합니다.

사용법 (각 노트북 상단에서):
    import sys, os
    sys.path.insert(0, os.path.abspath(''))

    import utils
    utils.reload_env()          # .env 재로드 (세션 중 변경 반영)

    from utils import (
        reload_env, uv_install, get_llm, test_llm_connection,
        LLM_PROVIDER, GOOGLE_API_KEY, ANTHROPIC_API_KEY, ANTHROPIC_OAUTH_TOKEN,
        VLLM_BASE_URL, VLLM_MODEL, OPENAI_API_KEY,
        print_provider_status,
        chunk_text, cosine_similarity,
        run_cmd, run_cmd_bg, tail_logs, stop_bg, list_bg,   # CMD 실행 (Windows/CMD/Docker)
    )
"""

import math
import os
import subprocess
import sys
import threading
import urllib.parse
from collections import deque
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv(override=True)

# =============================================================================
# 패키지 설치
# =============================================================================

def uv_install(packages: list):
    """uv가 있으면 uv pip install, 없으면 pip install로 폴백합니다."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        cmd = ["uv", "pip", "install"] + packages
        prefix = "uv"
    except (FileNotFoundError, subprocess.CalledProcessError):
        # cmd = [sys.executable, "-m", "pip", "install", "-q"] + packages
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        prefix = "pip"
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"[{prefix}] 설치 오류:\n{(result.stderr or '')[:500]}")
    else:
        print(f"[{prefix}] 설치 완료: {packages}")


# =============================================================================
# LLM 공급자 설정
# =============================================================================
#
# LLM_PROVIDER 선택 옵션:
#   --- 로컬 LLM 서버 (모두 OpenAI 호환 프로토콜) ---
#   "ollama"          → Ollama 서버 (http://localhost:11434/v1) ★ 본 강의 기본값(qwen3:8b)
#   "llamacpp"        → llama.cpp 서버 (llama-cpp-python, Windows 네이티브 / WSL 불필요)
#   "vllm"            → vLLM 서버 (Linux/GPU 권장; Windows+Docker 는 비권장)
#   --- 클라우드 (비교/대체용 — .env 한 줄 전환) ---
#   "google"          → Google AI Studio (무료, Gemini) ★ 기본 비교 대상
#   "anthropic"       → Anthropic API Key (Claude Haiku)
#   "anthropic_oauth" → Anthropic OAuth Bearer Token
#   "openai"          → OpenAI API (GPT-4o-mini)
#
# 본 강의 기본 구성: 로컬 Ollama + qwen3:8b 를 기본 LLM 으로 사용하고,
# Google(Gemini) 을 손쉬운 비교 대상으로 둡니다. .env 의 LLM_PROVIDER 한 줄만
# ollama ↔ google 로 바꾸면 로컬/클라우드를 즉시 전환할 수 있습니다.
#
# .env 파일에 다음 변수를 설정하세요:
#   LLM_PROVIDER=ollama
#   OLLAMA_BASE_URL=http://localhost:11434/v1
#   OLLAMA_MODEL=qwen3:8b
#   GOOGLE_API_KEY=...            # google 로 전환 시 필요
#   ANTHROPIC_API_KEY=...
#   ANTHROPIC_OAUTH_TOKEN=...
#   OPENAI_API_KEY=...
#   LLAMACPP_BASE_URL=http://localhost:8000/v1
#   LLAMACPP_MODEL=llamacpp
#   VLLM_BASE_URL=http://localhost:8000/v1
#   VLLM_MODEL=meta-llama/Llama-3.1-8B-Instruct

LLM_PROVIDER          = os.getenv("LLM_PROVIDER", "ollama")
GOOGLE_API_KEY        = os.getenv("GOOGLE_API_KEY", "")
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_OAUTH_TOKEN = os.getenv("ANTHROPIC_OAUTH_TOKEN", "")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")
# 로컬 LLM 서버 (OpenAI 호환)
LLAMACPP_BASE_URL     = os.getenv("LLAMACPP_BASE_URL", "http://localhost:8000/v1")
LLAMACPP_MODEL        = os.getenv("LLAMACPP_MODEL", "llamacpp")
OLLAMA_BASE_URL       = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL          = os.getenv("OLLAMA_MODEL", "qwen3:8b")
VLLM_BASE_URL         = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_MODEL            = os.getenv("VLLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
# NVIDIA build (build.nvidia.com) — 무료 크레딧, langchain-nvidia-ai-endpoints 의 ChatNVIDIA
NVIDIA_API_KEY        = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL       = os.getenv("NVIDIA_BASE_URL", "")  # 비우면 ChatNVIDIA 기본 엔드포인트
NVIDIA_MODEL          = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
# OpenRouter (openrouter.ai) — 무료 모델 라우터, OpenAI 호환 프로토콜(ChatOpenAI + base_url)
OPENROUTER_API_KEY    = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL   = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# 기본은 무료 모델 자동 선택 라우터(openrouter/free). 특정 free 모델로 고정하려면 .env 에서 변경.
OPENROUTER_MODEL      = os.getenv("OPENROUTER_MODEL", "openrouter/free")


def reload_env():
    """
    .env 파일을 재로드하고 모듈 전역 변수를 갱신합니다.
    노트북 세션 중 .env를 수정했을 때 호출하면 즉시 반영됩니다.
    """
    global LLM_PROVIDER, GOOGLE_API_KEY, ANTHROPIC_API_KEY, ANTHROPIC_OAUTH_TOKEN
    global VLLM_BASE_URL, VLLM_MODEL, OPENAI_API_KEY
    global LLAMACPP_BASE_URL, LLAMACPP_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL
    global NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL
    global OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

    load_dotenv(override=True)

    LLM_PROVIDER          = os.getenv("LLM_PROVIDER", "ollama")
    GOOGLE_API_KEY        = os.getenv("GOOGLE_API_KEY", "")
    ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_OAUTH_TOKEN = os.getenv("ANTHROPIC_OAUTH_TOKEN", "")
    OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")
    LLAMACPP_BASE_URL     = os.getenv("LLAMACPP_BASE_URL", "http://localhost:8000/v1")
    LLAMACPP_MODEL        = os.getenv("LLAMACPP_MODEL", "llamacpp")
    OLLAMA_BASE_URL       = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL          = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    VLLM_BASE_URL         = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
    VLLM_MODEL            = os.getenv("VLLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    NVIDIA_API_KEY        = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL       = os.getenv("NVIDIA_BASE_URL", "")
    NVIDIA_MODEL          = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
    OPENROUTER_API_KEY    = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL   = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL      = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    print_provider_status()


def print_provider_status():
    """현재 LLM 공급자와 키 설정 상태를 출력합니다."""
    print(f"LLM 공급자: {LLM_PROVIDER}")
    if LLM_PROVIDER == "google":
        status = "설정됨" if GOOGLE_API_KEY else "미설정 — .env에 GOOGLE_API_KEY 추가"
        print(f"  Google API Key: {status}")
    elif LLM_PROVIDER == "anthropic":
        status = "설정됨" if ANTHROPIC_API_KEY else "미설정 — .env에 ANTHROPIC_API_KEY 추가"
        print(f"  Anthropic API Key: {status}")
    elif LLM_PROVIDER == "anthropic_oauth":
        status = "설정됨" if ANTHROPIC_OAUTH_TOKEN else "미설정 — .env에 ANTHROPIC_OAUTH_TOKEN 추가"
        print(f"  OAuth Token: {status}")
    elif LLM_PROVIDER == "vllm":
        print(f"  vLLM URL: {VLLM_BASE_URL}  /  Model: {VLLM_MODEL}")
    elif LLM_PROVIDER == "llamacpp":
        print(f"  llama.cpp URL: {LLAMACPP_BASE_URL}  /  Model: {LLAMACPP_MODEL}")
    elif LLM_PROVIDER == "ollama":
        print(f"  Ollama URL: {OLLAMA_BASE_URL}  /  Model: {OLLAMA_MODEL}")
    elif LLM_PROVIDER == "openai":
        status = "설정됨" if OPENAI_API_KEY else "미설정 — .env에 OPENAI_API_KEY 추가"
        print(f"  OpenAI Key: {status}")
    elif LLM_PROVIDER == "nvidia":
        status = "설정됨" if NVIDIA_API_KEY else "미설정 — build.nvidia.com 에서 NVIDIA_API_KEY 발급"
        print(f"  NVIDIA build Key: {status}  /  Model: {NVIDIA_MODEL}")
    elif LLM_PROVIDER == "openrouter":
        status = "설정됨" if OPENROUTER_API_KEY else "미설정 — openrouter.ai 에서 OPENROUTER_API_KEY 발급"
        print(f"  OpenRouter Key: {status}  /  Model: {OPENROUTER_MODEL}")
    else:
        print(f"  알 수 없는 공급자: {LLM_PROVIDER}")


# =============================================================================
# LLM 팩토리
# =============================================================================

def get_llm(provider: str = None, temperature: float = 0):
    """
    공급자(provider)에 맞는 LangChain BaseChatModel 인스턴스를 반환합니다.

    Args:
        provider: LLM 공급자. None이면 LLM_PROVIDER 환경변수 사용.
        temperature: 생성 온도 (0 = 결정론적).

    Returns:
        langchain_core.language_models.BaseChatModel
    """
    p = provider or LLM_PROVIDER

    if p == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",
            google_api_key=GOOGLE_API_KEY,
            temperature=temperature,
        )
    elif p == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=1024,
        )
    elif p == "anthropic_oauth":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=ANTHROPIC_OAUTH_TOKEN,
            default_headers={"Authorization": f"Bearer {ANTHROPIC_OAUTH_TOKEN}"},
            temperature=temperature,
            max_tokens=1024,
        )
    elif p == "vllm":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=VLLM_MODEL,
            base_url=VLLM_BASE_URL,
            api_key="EMPTY",
            temperature=temperature,
            max_tokens=1024,
        )
    elif p == "llamacpp":
        # llama.cpp 서버(llama-cpp-python)의 OpenAI 호환 엔드포인트. api_key 는 형식상 임의 값.
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=LLAMACPP_MODEL,
            base_url=LLAMACPP_BASE_URL,
            api_key="sk-no-key-required",
            temperature=temperature,
            max_tokens=1024,
        )
    elif p == "ollama":
        # Ollama 의 OpenAI 호환 엔드포인트(/v1). api_key 는 형식상 임의 값.
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",
            temperature=temperature,
            max_tokens=1024,
        )
    elif p == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=temperature,
            max_tokens=1024,
        )
    elif p == "nvidia":
        # NVIDIA build (build.nvidia.com) — 무료 크레딧. langchain 커넥터 ChatNVIDIA 사용.
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        kwargs = dict(model=NVIDIA_MODEL, api_key=NVIDIA_API_KEY,
                      temperature=temperature, max_tokens=1024)
        if NVIDIA_BASE_URL:                    # 지정 시에만 엔드포인트 오버라이드
            kwargs["base_url"] = NVIDIA_BASE_URL
        return ChatNVIDIA(**kwargs)
    elif p == "openrouter":
        # OpenRouter (openrouter.ai) — OpenAI 호환 엔드포인트. 기본 모델은 무료 라우터(openrouter/free).
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=OPENROUTER_MODEL,
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
            temperature=temperature,
            max_tokens=1024,
        )

    raise ValueError(
        f"지원하지 않는 LLM 공급자: {p!r}. "
        "사용 가능: google, anthropic, anthropic_oauth, openai, llamacpp, ollama, vllm, nvidia, openrouter"
    )


def test_llm_connection() -> Optional[object]:
    """
    LLM 연결을 테스트하고 성공 시 모델 인스턴스를 반환합니다.

    Returns:
        연결 성공 시 BaseChatModel, 실패 시 None.
    """
    try:
        m = get_llm()
        from langchain_core.messages import HumanMessage
        resp = m.invoke([HumanMessage(content="1+1을 계산하면?")])
        content = resp.content if isinstance(resp.content, str) else str(resp.content)
        print(f"LLM 연결 성공 [{LLM_PROVIDER}]: {content[:80]}")
        return m
    except Exception as e:
        print(f"LLM 연결 실패 [{LLM_PROVIDER}]: {e}")
        print("  .env 파일의 API 키와 LLM_PROVIDER 설정을 확인하세요.")
        return None


# =============================================================================
# CMD 명령 실행 (Windows 11 + CMD + Docker Desktop, No WSL)
# =============================================================================
#
# 모든 노트북에서 셸(CMD) 명령을 주피터 셀 안에서 실행하기 위한 공통 함수입니다.
# 실행 환경은 Windows 11 + cmd.exe + Docker Desktop (WSL 미사용) 을 전제로 합니다.
# subprocess 가 shell=True 로 호출되므로 Windows 에서는 cmd.exe 가 사용됩니다.
#
# 사용 예 (노트북 셀):
#     import utils
#     utils.run_cmd("docker ps")                                  # 동기 실행 + 출력 스트리밍
#     utils.run_cmd_bg("docker logs -f vllm-server", "vllm-log")  # 백그라운드 실행
#     utils.tail_logs("vllm-log")    # 다른 셀에서 언제든 최근 로그 확인
#     utils.stop_bg("vllm-log")      # 백그라운드 프로세스 종료

# 이름 → 백그라운드 프로세스 핸들 레지스트리 (모든 노트북 셀에서 공유)
_BG_PROCS = {}


class _BgProc:
    """백그라운드로 실행되는 CMD 프로세스. stdout/stderr 를 데몬 스레드로 계속 수집해
    다른 셀이 실행 중이어도 tail() 로 최근 로그를 확인할 수 있게 한다."""

    def __init__(self, name: str, cmd: str, maxlines: int = 5000):
        self.name = name
        self.cmd = cmd
        self.proc = None
        self.lines = deque(maxlen=maxlines)   # 최근 로그만 보관 (메모리 보호)
        self._thread = None

    def start(self):
        # Windows 에서는 shell=True 가 cmd.exe 를 사용 (stderr 를 stdout 으로 합쳐 한 버퍼로 수집)
        self.proc = subprocess.Popen(
            self.cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, encoding="utf-8", errors="replace",
        )
        self._thread = threading.Thread(target=self._drain, daemon=True)
        self._thread.start()
        return self

    def _drain(self):
        """프로세스 출력을 한 줄씩 읽어 deque 에 적재한다 (백그라운드 스레드)."""
        for line in self.proc.stdout:
            self.lines.append(line.rstrip("\n"))

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def tail(self, n: int = 30) -> List[str]:
        return list(self.lines)[-n:]


def run_cmd(cmd: str, echo: bool = True, check: bool = False):
    """CMD 명령을 동기 실행하고 출력을 실시간 스트리밍한다.

    Args:
        cmd: 실행할 셸 명령 문자열 (Windows 면 cmd.exe 로 실행).
        echo: True 면 명령과 출력을 셀에 그대로 출력.
        check: True 면 0 이 아닌 종료 코드에서 RuntimeError 발생.

    Returns:
        (returncode, output) 튜플.
    """
    if echo:
        print(f"$ {cmd}")
    proc = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, encoding="utf-8", errors="replace",
    )
    out_lines = []
    for line in proc.stdout:
        line = line.rstrip("\n")
        out_lines.append(line)
        if echo:
            print(line)
    proc.wait()
    if check and proc.returncode != 0:
        raise RuntimeError(f"명령 실패 (rc={proc.returncode}): {cmd}")
    return proc.returncode, "\n".join(out_lines)


def run_cmd_bg(cmd: str, name: str):
    """CMD 명령을 백그라운드로 실행한다. 다른 셀 실행 중에도 tail_logs(name) 로 로그 확인 가능.

    같은 name 으로 실행 중인 프로세스가 있으면 먼저 종료한 뒤 새로 시작한다.

    Args:
        cmd: 실행할 셸 명령 문자열.
        name: 이 백그라운드 작업을 참조할 이름 (tail_logs / stop_bg 에서 사용).

    Returns:
        _BgProc 핸들.
    """
    stop_bg(name, quiet=True)               # 동일 이름 기존 프로세스 정리
    bp = _BgProc(name, cmd).start()
    _BG_PROCS[name] = bp
    print(f"[백그라운드 시작] name='{name}'\n$ {cmd}")
    print(f"  → 진행 로그는 다른 셀에서  utils.tail_logs('{name}')  로 확인하세요.")
    return bp


def tail_logs(name: str, n: int = 30):
    """백그라운드 프로세스의 최근 로그 n 줄과 실행 상태를 출력한다."""
    bp = _BG_PROCS.get(name)
    if not bp:
        print(f"[없음] '{name}' 백그라운드 프로세스가 없습니다. (run_cmd_bg 로 먼저 시작)")
        return
    state = "실행 중" if bp.is_running() else f"종료됨 (rc={bp.proc.returncode})"
    print(f"[{name}] 상태: {state}  ·  최근 {n}줄")
    print("-" * 60)
    for line in bp.tail(n):
        print(line)


def _terminate_tree(proc):
    """프로세스와 그 자식들(트리)을 종료한다.

    run_cmd_bg 는 shell=True(cmd.exe 래퍼)로 띄우므로, proc.terminate() 는 래퍼만 죽이고
    실제 서버(자식 python 등)가 살아남아 포트/GPU 를 점유한다. Windows 에서는 taskkill /T 로
    트리 전체를 종료해 이 누수를 막는다.
    """
    if proc is None:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True)
        else:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def stop_bg(name: str, quiet: bool = False):
    """백그라운드 프로세스(및 그 자식 프로세스)를 종료한다.

    shell 래퍼만이 아니라 실제 서버까지 함께 종료하므로, 재기동 시 포트/GPU 충돌이 없다.
    """
    bp = _BG_PROCS.pop(name, None)
    if not bp:
        if not quiet:
            print(f"[없음] '{name}' 등록된 백그라운드 프로세스가 없습니다.")
        return
    _terminate_tree(bp.proc)
    if not quiet:
        print(f"[중지] name='{name}' (자식 프로세스 포함)")


def list_bg():
    """현재 등록된 백그라운드 프로세스 목록과 상태를 출력한다."""
    if not _BG_PROCS:
        print("등록된 백그라운드 프로세스가 없습니다.")
        return
    for name, bp in _BG_PROCS.items():
        state = "실행 중" if bp.is_running() else f"종료됨 (rc={bp.proc.returncode})"
        print(f"  {name:20s} {state}   $ {bp.cmd}")


# =============================================================================
# 텍스트 처리 유틸리티
# =============================================================================

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """텍스트를 겹치는 청크로 분할합니다."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """두 벡터의 코사인 유사도를 계산합니다."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a ** 2 for a in vec1))
    mag2 = math.sqrt(sum(b ** 2 for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)
