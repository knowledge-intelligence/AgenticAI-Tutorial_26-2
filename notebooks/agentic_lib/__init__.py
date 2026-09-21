"""
agentic_lib — Agentic AI Tutorial 공통 라이브러리
=================================================

여러 노트북에서 반복적으로 사용하거나, 길어서 노트북 셀을 어지럽히는 코드를
모듈별 파이썬 파일로 분리해 둔 패키지입니다. 노트북은 핵심 '개념'에 집중하고,
세부 구현은 이 라이브러리를 import 해서 재사용합니다.

모듈 구성:
    bootstrap   노트북 공통 셋업, LLM 응답 텍스트 정규화(to_text), <think> 제거
    tools       공통 LangChain 도구(@tool): calculator / get_current_time / search_web / get_weather / 파일 IO
    memory      에이전트 메모리: 단기(ConversationMemory) / 장기(SimpleVectorMemory) 등
    agent_memory  지식 에이전트 4계층 메모리(단기/일화/의미/작업) + DeepKnowledgeAgent
    planning    작업 계획·실행: Task / TaskStatus / TaskPlanner
    react       LLM 없이 동작 원리를 보여주는 SimpleReActAgent(ReAct 패턴 시뮬레이션)
    embeddings  임베딩 공급자 추상화: get_embedder(local/google/nvidia/openrouter/ollama) + 벤치마크
    doc_prep    문서 전처리: 구조화(front matter·섹션) / 청킹 4전략 / 메타데이터 설계
    vector_stores  벡터 DB 통일 어댑터: ChromaDB / FAISS / Qdrant
    lc_rag      LangChain RAG: PromptTemplate / LCEL 체인 / 검색 도구 / RAG Agent
    llama_rag   LlamaIndex RAG·GraphRAG: 공급자 어댑터 / VectorStoreIndex / PropertyGraphIndex
    rag         RAG·지식 그래프: VectorRAG / KnowledgeGraph / Neo4jVectorStore / HybridRAG

사용 예 (노트북 셀):
    import sys, os
    sys.path.insert(0, os.path.abspath(''))      # notebooks/ 를 import 경로에 추가
    from agentic_lib import bootstrap, tools, memory, planning

    llm = bootstrap.setup()                       # .env 재로드 + 기본 LLM(ollama/qwen3:8b) 반환
    text = bootstrap.invoke_text(llm, "안녕?")    # 응답을 항상 깔끔한 문자열로
"""

# 자주 쓰는 심볼은 패키지 최상위에서 바로 import 할 수 있도록 노출한다.
from .bootstrap import (
    setup, invoke_text, to_text, strip_think,
)

__all__ = [
    "setup", "invoke_text", "to_text", "strip_think",
]
