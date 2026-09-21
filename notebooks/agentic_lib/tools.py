"""
tools — 여러 노트북이 공유하는 LangChain 도구 모음
===================================================

에이전트 실습에서 반복적으로 정의하던 도구(@tool)들을 한곳에 모았습니다.
LangChain `@tool` 데코레이터로 감싼 함수라서 `llm.bind_tools(...)` 나
`create_agent(...)` 에 그대로 넘길 수 있습니다.

제공 도구:
    calculator(expression)      안전한 수식 계산 (math 함수 허용, '^'는 거듭제곱으로 보정)
    get_current_time()          현재 날짜·시간 문자열
    search_web(query)           실제 웹 검색 (DuckDuckGo/ddgs, 키 불필요; 실패 시 시뮬레이션 폴백)
    get_weather(city)           실제 날씨 조회 (Open-Meteo, 키 불필요; 실패 시 시뮬레이션 폴백)
    read_text_file(path)        텍스트 파일 읽기 (작업 폴더 안으로 제한)
    write_text_file(path, text) 텍스트 파일 쓰기 (작업 폴더 안으로 제한)

실제 외부 서비스 호출 도구(search_web/get_weather)는 모두 **무료·API 키 불필요** 서비스를
사용하며, 오프라인·레이트리밋 시 시뮬레이션으로 자동 폴백한다. 결정론적(재현 가능) 실행이
필요하면 환경변수로 시뮬레이션을 강제할 수 있다: `WEB_SEARCH_MODE=sim`, `WEATHER_MODE=sim`.

편의 변수:
    BASIC_TOOLS   = [calculator, get_current_time, search_web]
    AGENT_TOOLS   = BASIC_TOOLS + [get_weather]
    FILE_TOOLS    = [read_text_file, write_text_file]
"""

import datetime
import math
import os

from langchain_core.tools import tool

# eval 에 노출할 안전한 math 심볼 집합. __builtins__ 를 비워 위험 함수 호출을 차단하고,
# 자주 쓰는 수학 함수/상수만 화이트리스트로 제공한다(예: sqrt(144), pi, sin(...)).
_SAFE_MATH = {
    name: getattr(math, name)
    for name in [
        "sqrt", "pow", "exp", "log", "log10", "log2",
        "sin", "cos", "tan", "asin", "acos", "atan",
        "floor", "ceil", "fabs", "factorial", "gcd",
        "degrees", "radians", "pi", "e", "tau",
    ]
}


def _safe_eval(expression: str) -> str:
    """수식 문자열을 안전하게 평가해 'expr = result' 형태로 돌려준다.

    - `__builtins__` 를 제거하고 _SAFE_MATH 만 노출해 임의 코드 실행을 막는다.
    - LLM 이 자주 쓰는 캐럿(^)을 Python 거듭제곱(**)으로 보정한다.
      (Python 에서 2^10 은 XOR=8 이 되어 흔한 오답을 유발하므로 미리 변환)
    """
    expr = expression.replace("^", "**")
    result = eval(expr, {"__builtins__": {}}, _SAFE_MATH)  # noqa: S307 (화이트리스트로 안전)
    return f"{expression} = {result}"


@tool
def calculator(expression: str) -> str:
    """수학 수식을 계산합니다. 예: '2 ** 10', 'sqrt(144)', '(3+4)*5'.

    Python 수식 문법을 사용하며 sqrt, sin, log, pi 같은 math 함수/상수를 쓸 수 있습니다.
    """
    try:
        return _safe_eval(expression)
    except Exception as e:
        return f"오류: {e}"


@tool
def get_current_time(dummy: str = "") -> str:
    """현재 날짜와 시간을 'YYYY-MM-DD HH:MM:SS' 형식으로 반환합니다.

    인자가 없는 도구를 허용하지 않는 일부 공급자를 위해 사용하지 않는 dummy 인자를 둡니다.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _sim_search(query: str) -> str:
    """오프라인/재현성용 가짜 검색 결과(고정 문자열)를 반환한다."""
    return f"'{query}' 검색 완료: 관련 최신 정보 3건 발견 (시뮬레이션)"


def _ddg_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo(ddgs)로 실제 웹 검색을 수행해 상위 결과를 요약 문자열로 반환한다.

    ddgs 는 API 키가 필요 없는 무료 검색 라이브러리다(CMD: `uv pip install ddgs`).
    반환 형식: 제목 / 요약(본문 앞부분) / URL 을 상위 max_results 건까지 정리한 텍스트.
    """
    from ddgs import DDGS  # 지연 import: 미설치 환경에서도 모듈 로드는 되도록
    with DDGS() as ddgs:
        hits = list(ddgs.text(query, max_results=max_results))
    if not hits:
        return f"'{query}' 에 대한 검색 결과가 없습니다."
    lines = [f"'{query}' 웹 검색 결과 상위 {len(hits)}건:"]
    for i, h in enumerate(hits, 1):
        title = h.get("title", "").strip()
        body = (h.get("body", "") or "").strip().replace("\n", " ")[:160]
        href = h.get("href", "")
        lines.append(f"{i}. {title}\n   {body}\n   {href}")
    return "\n".join(lines)


@tool
def search_web(query: str) -> str:
    """웹을 검색합니다. 기본은 DuckDuckGo 실제 검색이며, 오프라인/실패 시 시뮬레이션으로 폴백합니다.

    - DuckDuckGo(ddgs)는 API 키가 필요 없습니다.
    - 재현 가능한 결정론적 실행을 원하면 환경변수 `WEB_SEARCH_MODE=sim` 로 시뮬레이션을 강제하세요.
    - ddgs 미설치·네트워크 차단·레이트리밋 시에는 자동으로 시뮬레이션 결과로 폴백합니다.
    """
    if os.getenv("WEB_SEARCH_MODE", "live").lower() == "sim":
        return _sim_search(query)
    try:
        return _ddg_search(query)
    except Exception as e:
        # 미설치/오프라인/레이트리밋 등은 예외를 흡수하고 시뮬레이션으로 자연 폴백
        return f"{_sim_search(query)}  [실제 검색 폴백: {type(e).__name__}]"


# 오프라인 폴백용 고정 날씨 데이터(도시 → 설명). 미등록 도시는 기본값을 사용한다.
_WEATHER_DB = {
    "서울": "맑음, 22도",
    "부산": "흐림, 24도",
    "제주": "비, 19도",
    "도쿄": "맑음, 25도",
    "뉴욕": "구름조금, 18도",
}

# WMO 날씨 코드 → 한글 설명 (Open-Meteo 표준 코드표)
_WMO_CODES = {
    0: "맑음",
    1: "대체로 맑음", 2: "부분적 흐림", 3: "흐림",
    45: "안개", 48: "짙은 안개(서리)",
    51: "약한 이슬비", 53: "이슬비", 55: "강한 이슬비",
    56: "약한 어는 이슬비", 57: "강한 어는 이슬비",
    61: "약한 비", 63: "비", 65: "강한 비",
    66: "약한 어는 비", 67: "강한 어는 비",
    71: "약한 눈", 73: "눈", 75: "강한 눈", 77: "싸락눈",
    80: "약한 소나기", 81: "소나기", 82: "강한 소나기",
    85: "약한 눈소나기", 86: "강한 눈소나기",
    95: "뇌우", 96: "우박 동반 뇌우", 99: "강한 우박 동반 뇌우",
}


# 주요 도시 좌표(위도, 경도). Open-Meteo 지오코딩이 한글 지명에 약해(예: '서울' 미검색,
# '부산' 오매칭) 흔한 도시는 좌표를 직접 매핑하고, 그 외 도시만 지오코딩 API 로 조회한다.
_CITY_COORDS = {
    "서울": (37.5665, 126.9780), "부산": (35.1796, 129.0756),
    "인천": (37.4563, 126.7052), "대구": (35.8714, 128.6014),
    "대전": (36.3504, 127.3845), "광주": (35.1595, 126.8526),
    "울산": (35.5384, 129.3114), "수원": (37.2636, 127.0286),
    "제주": (33.4996, 126.5312),
    "도쿄": (35.6762, 139.6503), "뉴욕": (40.7128, -74.0060),
    "런던": (51.5074, -0.1278), "파리": (48.8566, 2.3522),
    "베이징": (39.9042, 116.4074), "상하이": (31.2304, 121.4737),
}


def _sim_weather(city: str) -> str:
    """오프라인/재현성용 가짜 날씨(고정 데이터)를 반환한다."""
    return f"{city} 날씨: {_WEATHER_DB.get(city, '맑음, 21도')} (시뮬레이션)"


def _open_meteo_weather(city: str, timeout: int = 10) -> str:
    """Open-Meteo(무료·API 키 불필요)로 도시의 현재 날씨를 조회한다.

    1) 지오코딩 API 로 도시명 → 위경도 변환(한국어 지명 지원)
    2) forecast API 로 현재 기온·날씨코드·풍속 조회
    3) WMO 날씨 코드를 한글 설명으로 변환
    """
    import requests  # 지연 import: 미설치 환경에서도 모듈 로드는 되도록
    # 1) 도시명 → 위경도: 주요 도시는 좌표표에서, 그 외는 지오코딩 API 로 조회
    key = city.strip()
    if key in _CITY_COORDS:
        lat, lon = _CITY_COORDS[key]
        name = key
    else:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": key, "count": 1, "language": "ko", "format": "json"},
            timeout=timeout,
        ).json()
        results = geo.get("results") or []
        if not results:
            raise ValueError(f"도시를 찾을 수 없음: {city}")
        loc = results[0]
        lat, lon = loc["latitude"], loc["longitude"]
        name = loc.get("name", key)
    # 2) 현재 날씨 조회
    wx = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
        },
        timeout=timeout,
    ).json()
    cur = wx["current"]
    # 3) WMO 코드 → 한글 설명 (name 은 위 1단계에서 이미 설정됨)
    desc = _WMO_CODES.get(cur["weather_code"], "알 수 없음")
    return (f"{name} 날씨: {desc}, {cur['temperature_2m']}°C "
            f"(풍속 {cur['wind_speed_10m']}m/s)")


@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 조회합니다(무료 Open-Meteo, API 키 불필요). 예: '서울', '부산'.

    - 기본은 실제 조회(Open-Meteo). 결정론적 실행이 필요하면 `WEATHER_MODE=sim` 으로 시뮬레이션을 강제하세요.
    - 네트워크 차단·도시 미검색·레이트리밋 시에는 자동으로 시뮬레이션으로 폴백합니다.
    """
    if os.getenv("WEATHER_MODE", "live").lower() == "sim":
        return _sim_weather(city)
    try:
        return _open_meteo_weather(city)
    except Exception as e:
        return f"{_sim_weather(city)}  [실제 조회 폴백: {type(e).__name__}]"


def _resolve_in_workspace(path: str) -> str:
    """파일 경로를 현재 작업 폴더 하위로 제한해 절대경로로 변환한다(경로 탈출 방지)."""
    base = os.path.abspath(os.getcwd())
    target = os.path.abspath(os.path.join(base, path))
    if not target.startswith(base):
        raise ValueError("작업 폴더 밖의 경로에는 접근할 수 없습니다.")
    return target


@tool
def write_text_file(path: str, content: str) -> str:
    """텍스트를 파일에 씁니다(현재 작업 폴더 하위만 허용). 상위 폴더는 자동 생성됩니다."""
    try:
        target = _resolve_in_workspace(path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"'{path}' 저장 완료 ({len(content)}자)"
    except Exception as e:
        return f"오류: {e}"


@tool
def read_text_file(path: str) -> str:
    """텍스트 파일을 읽어 내용을 반환합니다(현재 작업 폴더 하위만 허용)."""
    try:
        target = _resolve_in_workspace(path)
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"오류: {e}"


# 노트북에서 바로 bind_tools 에 넘길 수 있는 묶음들
BASIC_TOOLS = [calculator, get_current_time, search_web]
AGENT_TOOLS = BASIC_TOOLS + [get_weather]
FILE_TOOLS = [read_text_file, write_text_file]
