"""
memory — 에이전트 메모리 기본 구현
==================================

에이전트의 '기억' 역량을 보여주는 기본 메모리 클래스들입니다. 여러 노트북에서
반복 정의되던 단기/장기 메모리를 한곳에 모았습니다(심화 패턴은 week09-11 메모리
노트북에서 추가로 다룹니다).

    ConversationMemory   단기 기억: 최근 N개 메시지만 유지하는 슬라이딩 윈도우 버퍼
    SimpleVectorMemory   장기 기억(시뮬레이션): 키워드 매칭 기반 저장/검색
                          (실제 운영에서는 ChromaDB·Pinecone 같은 벡터 DB 사용)
"""

from collections import deque
from typing import Dict, List


class ConversationMemory:
    """단기 기억 — 최근 대화만 유지하는 슬라이딩 윈도우 버퍼.

    deque(maxlen=N) 을 사용해, 메시지가 N개를 넘으면 가장 오래된 것이 자동으로 밀려난다.
    토큰 한도가 있는 LLM 에 '최근 맥락'만 넘길 때 쓰는 가장 단순한 메모리 형태다.
    """

    def __init__(self, max_messages: int = 10):
        """버퍼를 생성한다.

        Args:
            max_messages: 보관할 최대 메시지 수(초과 시 오래된 것부터 폐기).
        """
        self.messages: deque = deque(maxlen=max_messages)

    def add(self, role: str, content: str) -> None:
        """메시지를 추가한다.

        Args:
            role: 발화 주체("user" / "assistant" / "system" 등).
            content: 메시지 내용.
        """
        self.messages.append({"role": role, "content": content})

    def get(self) -> List[Dict]:
        """현재 보관 중인 메시지 목록(오래된 → 최신 순)을 반환한다."""
        return list(self.messages)

    def clear(self) -> None:
        """버퍼를 비운다."""
        self.messages.clear()


class SimpleVectorMemory:
    """장기 기억(시뮬레이션) — 키워드 매칭으로 저장/검색하는 간이 메모리.

    실제로는 임베딩 + 벡터 유사도 검색(ChromaDB 등)을 쓰지만, 여기서는 개념 이해를
    위해 부분 문자열 매칭으로 단순화했다. 저장 항목은 {key, value, metadata} 형태다.
    """

    def __init__(self):
        self.storage: List[Dict] = []

    def save(self, key: str, value: str, metadata: dict = None) -> None:
        """항목을 저장한다.

        Args:
            key: 검색용 식별자/제목.
            value: 저장할 본문.
            metadata: 부가 정보(선택).
        """
        self.storage.append({"key": key, "value": value, "metadata": metadata or {}})
        print(f"[저장] '{key}'")

    def search(self, query: str) -> List[Dict]:
        """key 또는 value 에 query(대소문자 무시)가 포함된 항목을 모두 반환한다."""
        q = query.lower()
        return [
            e for e in self.storage
            if q in e["key"].lower() or q in e["value"].lower()
        ]
