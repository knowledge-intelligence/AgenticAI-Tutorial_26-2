"""
bootstrap — 노트북 공통 셋업 & LLM 응답 정규화
==============================================

모든 노트북이 첫 셀에서 반복하던 셋업(.env 재로드 → LLM 생성)과,
공급자마다 제각각인 응답 형식을 '깔끔한 문자열'로 통일하는 헬퍼를 모았습니다.

왜 필요한가?
    - LangChain 의 `response.content` 는 공급자마다 형식이 다르다.
        * Google(Gemini)  : list[dict]  예) [{'type':'text','text':'...', 'extras': {...}}]
        * Ollama(qwen3:8b): str          예) "<think> ... </think>\\n실제 답변"
        * Anthropic        : list[dict]  예) [{'type':'text','text':'...'}]
      그대로 print 하면 `[{'type':'text', ...}]` 또는 `[]` 처럼 지저분하게 나온다.
    - qwen3 같은 '사고(thinking) 모델' 은 답변 앞에 <think>...</think> 추론 과정을 붙인다.
      교육용 출력에서는 이 부분을 떼고 최종 답변만 보여주는 편이 깔끔하다.

→ `to_text()` 하나로 어떤 공급자든 동일하게 처리한다.
"""

import os
import re
import sys

# notebooks/ 디렉터리를 import 경로에 넣어 형제 모듈 utils.py 를 찾을 수 있게 한다.
# (노트북에서 이미 sys.path 에 넣지만, 라이브러리 단독 import 시에도 안전하도록 보강)
_HERE = os.path.dirname(os.path.abspath(__file__))
_NOTEBOOKS_DIR = os.path.dirname(_HERE)
if _NOTEBOOKS_DIR not in sys.path:
    sys.path.insert(0, _NOTEBOOKS_DIR)

import utils  # noqa: E402  (경로 보강 후 import 해야 하므로 상단 정렬 예외)

# <think>...</think> 블록(사고 과정)을 찾는 정규식. re.DOTALL 로 줄바꿈 포함 매칭.
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_think(text: str) -> str:
    """qwen3 등 사고 모델의 <think>...</think> 추론 블록을 제거한다.

    Args:
        text: 원본 텍스트.

    Returns:
        <think> 블록을 제거하고 앞뒤 공백을 정리한 문자열.
    """
    return _THINK_RE.sub("", text).strip()


def to_text(content, strip_thinking: bool = True, strip: bool = True) -> str:
    """LangChain 메시지의 content 를 공급자와 무관하게 '평범한 문자열'로 정규화한다.

    Google/Anthropic 의 list[dict] 형식, Ollama 의 str 형식, dict 단일 형식을 모두 처리한다.

    Args:
        content: `response.content` (str | list | dict | None).
        strip_thinking: True 면 <think>...</think> 추론 블록을 제거한다(기본값).
        strip: True 면 앞뒤 공백을 제거한다(기본값). **스트리밍**에서 청크마다 호출할 때는
            False 로 둬야 한다 — 토큰 앞 공백(예: " 사용자")까지 잘려 단어가 붙어버리기 때문.

    Returns:
        화면 출력에 적합한 정돈된 문자열.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        # 각 파트가 dict 면 'text' 키를, 아니면 문자열화해서 이어 붙인다.
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            else:
                parts.append(str(part))
        text = "".join(parts)
    elif isinstance(content, dict):
        text = content.get("text", str(content))
    else:
        text = str(content)

    if strip_thinking:
        text = strip_think(text)   # strip_think 내부에서도 .strip() 하므로 사고블록 제거 시엔 정돈됨
    return text.strip() if strip else text


def invoke_text(llm, messages, strip_thinking: bool = True) -> str:
    """LLM 을 호출하고 응답을 곧바로 정규화된 문자열로 돌려준다.

    `to_text(llm.invoke(messages).content)` 의 단축형. 문자열을 주면
    HumanMessage 한 개로 감싸 호출한다.

    Args:
        llm: LangChain BaseChatModel.
        messages: 문자열 프롬프트 또는 LangChain 메시지 리스트.
        strip_thinking: <think> 블록 제거 여부.

    Returns:
        모델 응답 텍스트(문자열).
    """
    from langchain_core.messages import HumanMessage
    if isinstance(messages, str):
        messages = [HumanMessage(content=messages)]
    resp = llm.invoke(messages)
    return to_text(resp.content, strip_thinking=strip_thinking)


def setup(provider: str = None, temperature: float = 0, verbose: bool = True):
    """노트북 공통 셋업: .env 재로드 후 기본 LLM 인스턴스를 반환한다.

    각 노트북 첫 셀의 반복 코드(reload_env → get_llm)를 한 줄로 줄인다.

    Args:
        provider: 사용할 LLM 공급자. None 이면 .env 의 LLM_PROVIDER(기본 'ollama').
        temperature: 생성 온도(0 = 결정론적).
        verbose: True 면 현재 공급자/모델 상태를 출력한다.

    Returns:
        LangChain BaseChatModel.
    """
    utils.reload_env()  # .env 를 다시 읽어 모듈 전역(LLM_PROVIDER 등) 갱신 + 상태 출력
    llm = utils.get_llm(provider, temperature)
    if verbose:
        p = provider or utils.LLM_PROVIDER
        print(f"[setup] LLM 준비 완료 — 공급자='{p}'")
    return llm


# =============================================================================
# 도구 호출(function calling) 공급자 차이 흡수
# =============================================================================
#
# 일부 서버는 '한 응답에 도구를 하나만' 호출할 수 있다. 대표적으로 NVIDIA build 의
# `meta/llama-3.1-8b-instruct` 는 대화 이력(assistant 메시지)에 tool_calls 가 2개 이상
# 들어가면 프롬프트 템플릿 적용이 실패해 다음과 같은 500 오류를 낸다.
#
#   Exception: [500] Failed to apply prompt template:
#     invalid operation: This model only supports single tool-calls at once!
#
# 반면 Ollama(qwen3:8b)·Google(Gemini) 등은 한 응답에서 여러 도구를 병렬 호출해도 된다.
# 아래 헬퍼들은 이 차이를 흡수해, 단일 도구 서버에서는 '순차(단일) 도구 호출'로 동작하도록 한다.

# 한 응답에 도구를 '하나만' 호출할 수 있는 공급자 집합.
_SINGLE_TOOLCALL_PROVIDERS = {"nvidia"}


def supports_parallel_tool_calls(provider: str = None) -> bool:
    """공급자가 한 응답에서 여러 도구를 병렬 호출해도 되는지 여부를 돌려준다.

    Args:
        provider: LLM 공급자. None 이면 utils.LLM_PROVIDER(현재 설정) 사용.

    Returns:
        병렬 도구 호출이 안전하면 True, 단일 호출만 지원하면 False.
    """
    provider = provider or utils.LLM_PROVIDER
    return provider not in _SINGLE_TOOLCALL_PROVIDERS


def bind_tools(llm, tools, provider: str = None, **kwargs):
    """공급자 차이를 흡수하는 `bind_tools` 래퍼.

    NVIDIA build 의 `llama-3.1-8b` 처럼 '한 번에 도구 하나만' 지원하는 서버에는
    parallel_tool_calls=False 를 넘겨 애초에 다중 tool_calls 가 나오지 않도록 유도한다
    (파라미터를 받지 않는 공급자/버전은 자동으로 일반 bind_tools 로 폴백).

    서버가 이 파라미터를 무시하더라도 실제 안전장치는 cap_tool_calls() 이므로,
    이 래퍼는 왕복(round-trip)을 줄여 주는 최적화에 가깝다.

    Args:
        llm: LangChain BaseChatModel.
        tools: bind_tools 에 넘길 도구 목록(또는 OpenAI 함수 스키마 리스트).
        provider: LLM 공급자. None 이면 utils.LLM_PROVIDER.
        **kwargs: bind_tools 에 그대로 전달할 추가 인자.

    Returns:
        도구가 바인딩된 Runnable.
    """
    provider = provider or utils.LLM_PROVIDER
    if not supports_parallel_tool_calls(provider):
        try:
            return llm.bind_tools(tools, parallel_tool_calls=False, **kwargs)
        except (TypeError, ValueError):
            pass  # 해당 파라미터 미지원 → 일반 바인딩으로 폴백(cap_tool_calls 가 보완)
    return llm.bind_tools(tools, **kwargs)


def cap_tool_calls(resp, provider: str = None):
    """단일 도구 호출만 지원하는 공급자면 응답의 tool_calls 를 '첫 1개'로 줄여 돌려준다.

    다중 tool_calls 를 대화 이력에 남기면 NVIDIA build 등에서 500 오류가 나므로,
    첫 호출만 처리하고 나머지는 다음 턴에 모델이 다시 요청하도록 한다(순차 실행).
    잔여 additional_kwargs 없이 깔끔하게 직렬화되도록 새 AIMessage 로 감싸 돌려준다.

    병렬을 지원하는 공급자(ollama/google 등)이거나 호출이 1개 이하이면 원본을 그대로 돌려준다.
    따라서 이 함수는 도구 사용 루프에서 항상 호출해도 안전하다.

    Args:
        resp: llm_with_tools.invoke(...) 가 돌려준 AIMessage.
        provider: LLM 공급자. None 이면 utils.LLM_PROVIDER.

    Returns:
        (필요 시) tool_calls 를 1개로 제한한 AIMessage, 아니면 원본 resp.
    """
    from langchain_core.messages import AIMessage

    provider = provider or utils.LLM_PROVIDER
    tool_calls = getattr(resp, "tool_calls", None) or []
    if supports_parallel_tool_calls(provider) or len(tool_calls) <= 1:
        return resp
    # 첫 tool_call 만 담은 새 AIMessage — 이력에 단일 호출만 남겨 500 오류를 방지한다.
    return AIMessage(content=resp.content or "", tool_calls=tool_calls[:1])
