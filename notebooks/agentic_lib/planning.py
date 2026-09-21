"""
planning — 작업 계획·실행(Planning) 기본 구현
=============================================

에이전트의 'Planning' 역량을 보여주는 기본 클래스들입니다. 복잡한 목표를 여러
작업(Task)으로 나누고, 작업 간 의존성을 지켜 순서대로 실행합니다. week01(개념)과
week12-14 계획 실습에서 공통으로 사용합니다(심화 DAG 실행은 계획 노트북에서 확장).

    TaskStatus    작업 상태 enum (대기/진행중/완료/실패)
    Task          작업 1개를 표현하는 dataclass (id, 설명, 도구, 의존성, 상태, 결과)
    TaskPlanner   작업을 추가/표시하고, 의존성을 확인하며 순차 실행하는 플래너
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TaskStatus(Enum):
    """작업의 진행 상태."""
    PENDING = "대기"
    IN_PROGRESS = "진행중"
    DONE = "완료"
    FAILED = "실패"


@dataclass
class Task:
    """실행 계획의 작업 1개.

    Attributes:
        id: 1부터 시작하는 작업 번호.
        description: 작업 설명(도구에 전달되는 입력으로도 쓰임).
        tool: 사용할 도구 이름(없으면 단순 완료 처리).
        depends_on: 선행되어야 하는 작업 id 목록.
        status: 현재 상태(TaskStatus).
        result: 실행 결과 문자열.
    """
    id: int
    description: str
    tool: Optional[str] = None
    depends_on: list = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None


class TaskPlanner:
    """작업을 등록하고 의존성을 지켜 순차 실행하는 단순 플래너."""

    def __init__(self):
        self.tasks: List[Task] = []

    def add(self, desc: str, tool: str = None, depends_on: list = None) -> Task:
        """작업을 추가하고 생성된 Task 를 반환한다.

        Args:
            desc: 작업 설명.
            tool: 사용할 도구 이름(선택).
            depends_on: 선행 작업 id 목록(선택).
        """
        t = Task(len(self.tasks) + 1, desc, tool, depends_on or [])
        self.tasks.append(t)
        return t

    def show(self) -> None:
        """현재 계획(작업 목록과 상태)을 보기 좋게 출력한다."""
        print("=== 실행 계획 ===")
        for t in self.tasks:
            dep = f" (의존: {t.depends_on})" if t.depends_on else ""
            print(f"  [{t.status.value:4s}] Task {t.id}: {t.description}{dep}")

    def execute(self, tools: dict) -> None:
        """의존성을 확인하며 작업을 순서대로 실행한다.

        선행 작업이 모두 완료(DONE)된 경우에만 실행하고, 아니면 건너뛴다(FAILED).
        도구 실행 중 예외는 조용히 삼키지 않고 원인을 출력한다(디버깅 가능성 확보).

        Args:
            tools: {도구이름: 호출가능객체} 딕셔너리. 호출은 tools[name](description) 형태.
        """
        print("\n=== 실행 ===")
        for t in self.tasks:
            ok = all(self.tasks[i - 1].status == TaskStatus.DONE for i in t.depends_on)
            if not ok:
                t.status = TaskStatus.FAILED
                print(f"  Task {t.id} 스킵 (의존 미완료)")
                continue

            t.status = TaskStatus.IN_PROGRESS
            print(f"  Task {t.id}: {t.description}")
            if t.tool and t.tool in tools:
                try:
                    t.result = tools[t.tool](t.description)
                    t.status = TaskStatus.DONE
                    print(f"    → {t.result}")
                except Exception as e:
                    t.status = TaskStatus.FAILED
                    print(f"    → 실패: {type(e).__name__}: {e}")
            else:
                t.status = TaskStatus.DONE
                t.result = "완료"
                print(f"    → {t.result}")
