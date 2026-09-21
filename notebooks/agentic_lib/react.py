"""
react — ReAct 패턴 시뮬레이션 (LLM 없이 동작 원리 이해)
======================================================

ReAct(Reason + Act)는 에이전트의 핵심 사고 루프입니다:

    목표 → Thought(분석·결정) → Action(도구 실행) → Observation(결과 관찰) → ... → Final Answer

이 모듈의 `SimpleReActAgent` 는 LLM 을 호출하지 않고 규칙 기반으로 Thought 를
흉내 내어, 실제 LLM 없이도 루프의 흐름(생각→행동→관찰)을 또렷하게 보여줍니다.
실전용 LLM 기반 ReAct 에이전트는 week01 §10(create_agent) 및 이후 LangGraph 노트북에서 다룹니다.

    PLAIN_TOOLS         규칙 기반 에이전트가 호출하는 {이름: 함수} 도구 딕셔너리
    SimpleReActAgent    ReAct 루프를 시뮬레이션하는 교육용 에이전트
"""

import datetime
import math
import re

# SimpleReActAgent 가 직접 호출하는 '평범한 함수' 도구들.
# (LangChain @tool 이 아니라 순수 callable — 규칙 기반 시뮬레이션이므로 단순하게 둔다)
# get_current_time 은 인자 없이도(ReAct), 인자와 함께도(TaskPlanner) 호출될 수 있어 *args 로 허용.
PLAIN_TOOLS = {
    "calculator": lambda expr: f"{expr} = {eval(expr.replace('^', '**'), {'__builtins__': {}}, {'math': math})}",
    "get_current_time": lambda *args: datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"),
    "search_web": lambda query: f"'{query}' 검색 결과: 관련 정보 3건 발견 (시뮬레이션)",
}


class SimpleReActAgent:
    """ReAct 패턴을 규칙 기반으로 시뮬레이션하는 교육용 에이전트(LLM 독립적).

    think() 가 LLM 의 역할을 대신해 목표 문자열의 키워드로 도구를 고르고,
    act() 가 도구를 실행하며, run() 이 Thought→Action→Observation 루프를 출력한다.
    """

    def __init__(self, tools: dict = None, max_steps: int = 5):
        """에이전트를 생성한다.

        Args:
            tools: {도구이름: 함수} 딕셔너리. None 이면 PLAIN_TOOLS 사용.
            max_steps: 루프 최대 반복 횟수(무한 루프 방지).
        """
        self.tools = tools if tools is not None else PLAIN_TOOLS
        self.max_steps = max_steps

    def think(self, goal: str, observation: str = None) -> dict:
        """Thought 단계 — 목표 키워드로 다음 행동을 결정한다(실제로는 LLM 의 역할).

        Returns:
            {"tool": 도구이름, "input": 입력} 또는 도구가 필요 없으면 {"tool": None, "answer": ...}.
        """
        if "시간" in goal or "몇 시" in goal:
            return {"tool": "get_current_time", "input": ""}
        elif "계산" in goal or any(op in goal for op in ["+", "-", "*", "/", "**", "^"]):
            expr = re.search(r"[\d\s\+\-\*\/\^\(\)\.]+", goal)
            return {"tool": "calculator", "input": expr.group().strip() if expr else goal}
        elif "검색" in goal or "찾아" in goal:
            return {"tool": "search_web", "input": goal}
        return {"tool": None, "answer": f"'{goal}'에 대한 직접 답변입니다."}

    def act(self, tool_name: str, tool_input: str) -> str:
        """Action 단계 — 선택된 도구를 실행해 결과(Observation)를 반환한다."""
        if tool_name in self.tools:
            return self.tools[tool_name](tool_input) if tool_input else self.tools[tool_name]()
        return f"도구 '{tool_name}'을 찾을 수 없습니다."

    def run(self, goal: str) -> str:
        """ReAct 루프를 실행하며 각 단계를 출력하고 최종 답을 반환한다."""
        print(f"[목표] {goal}")
        print("-" * 50)
        observation = None
        for step in range(1, self.max_steps + 1):
            thought = self.think(goal, observation)
            print(f"[Thought {step}] 사용할 도구: {thought.get('tool', '없음')}")
            if thought.get("tool") is None:
                answer = thought.get("answer", "답변 불가")
                print(f"[Final Answer] {answer}")
                return answer
            print(f"[Action {step}] {thought['tool']}('{thought['input'][:40]}')")
            observation = self.act(thought["tool"], thought["input"])
            print(f"[Observation {step}] {observation}")
            print()
            if observation and "오류" not in observation:
                print(f"[Final Answer] {observation}")
                return observation
        return "최대 단계 도달"
