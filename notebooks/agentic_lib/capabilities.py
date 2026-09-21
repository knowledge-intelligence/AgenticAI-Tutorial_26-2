"""
capabilities — 4대 역량 심화: 구조화 출력 기반 Planning
======================================================

M01_2_core_capabilities 노트북의 'Planning(계획)' 심화 실습에서 쓰는,
길고 반복적인 구현을 분리해 둔 모듈입니다. 핵심은 LLM 의 **구조화 출력
(Structured Output)** 으로 자유 텍스트 대신 **Pydantic 스키마에 맞는 실행 계획**을
받아, 의존성 순서대로 자동 실행하는 것입니다.

    PlanStep        계획의 한 단계(번호/작업/도구/의존성/예상결과)를 담는 Pydantic 모델
    ExecutionPlan   목표 + 단계 목록 + 예상 소요시간을 담는 Pydantic 모델
    Status          단계 실행 상태 enum (대기/실행중/완료/건너뜀)
    execute_plan    계획을 의존성 순서대로 실행하는 함수(도구 또는 LLM 으로 단계 처리)

note:
    기존 `planning` 모듈(Task/TaskStatus/TaskPlanner)은 LLM 없이 동작하는 단순
    플래너이고, 이 모듈은 **LLM 의 with_structured_output 으로 계획을 생성**하는
    심화판입니다. 둘은 목적이 달라 별도로 둡니다.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from .bootstrap import to_text


class PlanStep(BaseModel):
    """실행 계획의 한 단계.

    LLM 이 with_structured_output(ExecutionPlan) 으로 채워 넣는 스키마라서,
    각 필드의 description 이 LLM 에게 '무엇을 채워야 하는지' 지시하는 역할을 한다.
    """
    step_num: int = Field(description="단계 번호 (1부터)")
    action: str = Field(description="수행할 구체적인 작업")
    tool: Optional[str] = Field(None, description="사용할 도구 이름 (없으면 null)")
    depends_on: List[int] = Field(default=[], description="의존하는 이전 단계 번호 목록")
    expected_output: str = Field(description="이 단계의 예상 결과물")


class ExecutionPlan(BaseModel):
    """LLM 이 생성하는 실행 계획 전체(목표 + 단계 목록 + 예상 소요시간)."""
    goal: str = Field(description="달성하려는 목표")
    steps: List[PlanStep] = Field(description="실행 단계 목록")
    estimated_duration: str = Field(description="예상 소요 시간")


class Status(Enum):
    """계획 단계의 실행 상태."""
    PENDING = "대기"
    RUNNING = "실행중"
    DONE = "완료"
    SKIPPED = "건너뜀"


def execute_plan(plan: ExecutionPlan, tool_map: dict, llm) -> dict:
    """계획의 각 단계를 의존성 순서에 따라 순차 실행한다.

    - 의존 단계가 모두 완료(DONE)된 경우에만 실행하고, 아니면 건너뛴다(SKIPPED).
    - 단계에 도구가 지정되어 있으면 도구를, 없으면 LLM 을 호출해 처리한다.
    - LLM 응답은 to_text() 로 정규화해 list-content/<think> 출력 문제를 없앤다.

    Args:
        plan: 실행할 ExecutionPlan(LLM 구조화 출력 결과).
        tool_map: {도구이름: LangChain 도구} 딕셔너리.
        llm: 도구가 없는 단계를 처리할 LangChain BaseChatModel.

    Returns:
        {단계번호: 결과문자열} 형태의 실행 결과 딕셔너리.
    """
    from langchain_core.messages import HumanMessage

    print(f"[목표] {plan.goal}\n")

    results: dict = {}
    statuses = {s.step_num: Status.PENDING for s in plan.steps}

    for step in plan.steps:
        # 의존성 미완료 → 건너뜀
        blocked = [d for d in step.depends_on if statuses.get(d) != Status.DONE]
        if blocked:
            statuses[step.step_num] = Status.SKIPPED
            print(f"[건너뜀] Step {step.step_num} — 의존 단계 미완료: {blocked}")
            continue

        statuses[step.step_num] = Status.RUNNING
        print(f"[실행중] Step {step.step_num}: {step.action}")

        if step.tool and step.tool in tool_map:
            # 도구가 지정된 단계: 도구를 직접 호출
            raw = tool_map[step.tool].invoke(step.action)
        else:
            # 도구가 없는 단계: 이전 단계 결과를 맥락으로 묶어 LLM 으로 처리
            context_lines = [
                f"이전 Step {d} 결과: {results[d]}"
                for d in step.depends_on if d in results
            ]
            prompt = step.action
            if context_lines:
                prompt += "\n\n참고:\n" + "\n".join(context_lines)
            raw = to_text(llm.invoke([HumanMessage(content=prompt)]).content)

        results[step.step_num] = raw
        statuses[step.step_num] = Status.DONE
        print(f"  → {str(raw)[:100]}")
        print()

    done_count = sum(1 for s in statuses.values() if s == Status.DONE)
    print(f"[완료] {done_count}/{len(plan.steps)} 단계 실행")
    return results
