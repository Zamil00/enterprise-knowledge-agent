from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    document_id: str
    top_k: int
    retrieved_chunks: List[Dict[str, Any]]
    analysis_summary: str
    final_answer: str
    evidence_quality: str
    should_block_answer: bool