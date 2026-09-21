"""
a2a — A2A(Agent-to-Agent) 협업 패턴 인프라
===========================================

모듈 1(연결) 노트북에서 다루는 A2A 3대 패턴의 골격 클래스를 모았습니다.
세 패턴 모두 LLM 없이 동작 원리를 보여 주는 교육용 시뮬레이션이며,
실제 의사결정(라우팅·의견 생성)은 데모에서 규칙/주입 함수로 대체합니다.

구성:
    BaseAgent          이름·역할·inbox/outbox 를 가진 에이전트 기본 클래스
    CoordinatorAgent   [계층형] 대장 에이전트가 하위 에이전트에 작업 분배
    PipelineAgent      [순차형] 컨베이어 벨트처럼 단계별로 데이터 변환
    SharedCanvas       [수평형] 에이전트들이 함께 쓰는 공유 작업 공간
    PeerAgent          [수평형] 공유 캔버스에 자기 전문 의견을 기여하는 동등 에이전트

세 패턴 비교:
    - 계층형: 중앙 집중식. 대장이 업무를 나눠 준다.
    - 순차형: 파이프라인. 한 에이전트의 출력이 다음의 입력이 된다.
    - 수평형: 협업. 동등한 에이전트들이 공유 공간에 함께 기여한다.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class BaseAgent:
    """에이전트 기본 클래스 — 이름·역할·메시지함(inbox/outbox)을 가진다."""

    def __init__(self, name: str, role: str, tools: Optional[dict] = None):
        self.name = name
        self.role = role
        self.tools = tools or {}
        self.inbox: List[Dict] = []   # 받은 메시지
        self.outbox: List[Dict] = []  # 보낸 메시지

    def receive(self, message: Dict):
        """다른 에이전트로부터 메시지를 받아 inbox 에 쌓는다."""
        self.inbox.append(message)

    def send(self, to: "BaseAgent", content: str, msg_type: str = "task") -> Dict:
        """대상 에이전트에게 메시지를 보내고(상대 inbox 적재) 기록을 남긴다."""
        message = {
            "from": self.name,
            "to": to.name,
            "type": msg_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        self.outbox.append(message)
        to.receive(message)
        print(f"  [{self.name}] → [{to.name}]: {content[:80]}")
        return message

    def process(self) -> str:
        """inbox 의 메시지를 하나 꺼내 처리한다(기본 구현은 단순 확인).

        하위 클래스에서 실제 처리 로직(도구 호출/LLM 등)으로 재정의할 수 있다.
        """
        if not self.inbox:
            return "대기 중"
        msg = self.inbox.pop(0)
        return f"[{self.name}] '{msg['content'][:50]}' 처리 완료"


class CoordinatorAgent(BaseAgent):
    """[계층형] 대장 에이전트 — 작업을 분석해 적절한 하위 에이전트에 분배한다."""

    def __init__(self, name: str, sub_agents: List[BaseAgent]):
        super().__init__(name, "coordinator")
        self.sub_agents = {a.name: a for a in sub_agents}  # 이름 → 하위 에이전트

    def delegate(self, task: str) -> Dict[str, str]:
        """태스크의 키워드를 보고 검색/계산/파일 하위 에이전트로 라우팅한다.

        실제 시스템에서는 이 라우팅 판단을 LLM 이 내리지만, 여기서는 동작 원리를
        보이기 위해 키워드 규칙으로 단순화한다.
        """
        results: Dict[str, str] = {}

        if "검색" in task or "찾아" in task:
            agent = self.sub_agents.get("SearchAgent")
            if agent:
                self.send(agent, f"검색 태스크: {task}")
                results["search"] = agent.process()

        if "계산" in task or any(op in task for op in ["+", "-", "*", "/"]):
            agent = self.sub_agents.get("CalculatorAgent")
            if agent:
                self.send(agent, f"계산 태스크: {task}")
                results["calc"] = agent.process()

        if "저장" in task or "파일" in task:
            agent = self.sub_agents.get("FileAgent")
            if agent:
                self.send(agent, f"파일 태스크: {task}")
                results["file"] = agent.process()

        return results


class PipelineAgent(BaseAgent):
    """[순차형] 파이프라인 한 단계를 담당하는 에이전트.

    processor(data) 로 입력을 변환하고, next_agent 가 있으면 그 출력을 넘긴다.
    """

    def __init__(self, name: str, role: str, processor: Callable):
        super().__init__(name, role)
        self.processor = processor                       # 이 단계의 변환 함수
        self.next_agent: Optional["PipelineAgent"] = None

    def set_next(self, agent: "PipelineAgent") -> "PipelineAgent":
        """다음 단계 에이전트를 연결하고 그 에이전트를 반환한다(체이닝 편의)."""
        self.next_agent = agent
        return agent

    def execute(self, data: Any) -> Any:
        """현재 단계를 처리하고, 다음 단계가 있으면 재귀적으로 이어 실행한다."""
        print(f"  [{self.name}({self.role})] 처리 중: {str(data)[:60]}")
        result = self.processor(data)
        print(f"    → 출력: {str(result)[:80]}")
        if self.next_agent:
            return self.next_agent.execute(result)
        return result


class SharedCanvas:
    """[수평형] 에이전트들이 함께 읽고 쓰는 공유 작업 공간."""

    def __init__(self):
        self.content: Dict[str, Any] = {}    # key → {value, author}
        self.messages: List[Dict] = []       # 작성 이력

    def write(self, agent_name: str, key: str, value: Any):
        """작성자 이름과 함께 값을 캔버스에 기록한다."""
        self.content[key] = {"value": value, "author": agent_name}
        self.messages.append({"agent": agent_name, "action": f"{key} 작성"})

    def read(self, key: str) -> Optional[Any]:
        """키에 해당하는 값을 읽는다(없으면 None)."""
        return self.content.get(key, {}).get("value")

    def get_summary(self) -> str:
        """캔버스 전체 내용을 보기 좋은 문자열로 요약한다."""
        lines = ["[공유 캔버스 현황]"]
        for key, data in self.content.items():
            lines.append(f"  [{data['author']}] {key}: {str(data['value'])[:60]}")
        return "\n".join(lines)


class PeerAgent(BaseAgent):
    """[수평형] 공유 캔버스에 자기 전문 분야 의견을 기여하는 동등 에이전트.

    의견 생성은 opinion_fn(expertise, topic) -> str 으로 주입한다. 데모에서는
    규칙 기반 함수를 넘기지만, LLM 을 감싼 클로저를 넘기면 실제 모델 의견을
    기여하게 할 수도 있다(이때 호출 측에서 to_text 로 정규화 권장).
    """

    def __init__(self, name: str, expertise: str, canvas: SharedCanvas,
                 opinion_fn: Optional[Callable[[str, str], str]] = None):
        super().__init__(name, expertise)
        self.expertise = expertise
        self.canvas = canvas
        self.opinion_fn = opinion_fn

    def contribute(self, topic: str) -> str:
        """주제에 대한 전문 의견을 만들어 공유 캔버스에 기록한다."""
        if self.opinion_fn is not None:
            contribution = self.opinion_fn(self.expertise, topic)
        else:
            contribution = f"{topic}에 대한 {self.expertise} 관점 의견"
        self.canvas.write(self.name, f"{self.expertise}_의견", contribution)
        print(f"  [{self.name}] 캔버스에 '{self.expertise}' 의견 추가")
        return contribution
