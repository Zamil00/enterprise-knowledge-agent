from openai import OpenAI
from app.config import get_settings
from app.core.state import AgentState
from app.services.retriever import retrieve
from app.services.report_formatter import format_context


ANALYSIS_PROMPT = """You are an evidence analyst for a document-grounded QA system.
Read the retrieved evidence and determine:
1. What is directly supported by evidence.
2. What is ambiguous or missing.
3. Whether the evidence is strong, medium, or weak.
Be concise and factual.
"""

REPORT_PROMPT = """You are a careful enterprise knowledge assistant.
Answer ONLY from the provided evidence. If evidence is insufficient, say so clearly.
Keep the answer concise, professional, and grounded.
"""


def _client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Create a .env file before querying.")
    return OpenAI(api_key=settings.openai_api_key)


def retrieval_agent(state: AgentState) -> AgentState:
    top_k = state.get("top_k") or get_settings().top_k_results
    document_id = state["document_id"]
    chunks = retrieve(state["question"], top_k=top_k, document_id=document_id)
    return {**state, "retrieved_chunks": chunks}


def analysis_agent(state: AgentState) -> AgentState:
    client = _client()
    settings = get_settings()
    chunks = state.get("retrieved_chunks", [])
    context = format_context(chunks)
    prompt = f"Question:\n{state['question']}\n\nEvidence:\n{context}"
    response = client.responses.create(
        model=settings.openai_chat_model,
        input=[
            {"role": "system", "content": ANALYSIS_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text.strip()
    lower = text.lower()
    evidence_quality = "medium"
    if "weak" in lower or "insufficient" in lower:
        evidence_quality = "weak"
    elif "strong" in lower:
        evidence_quality = "strong"
    should_block = evidence_quality == "weak" or len(chunks) == 0
    return {
        **state,
        "analysis_summary": text,
        "evidence_quality": evidence_quality,
        "should_block_answer": should_block,
    }


def report_agent(state: AgentState) -> AgentState:
    if state.get("should_block_answer"):
        answer = "I do not have enough reliable evidence in the uploaded documents to answer this confidently."
        return {**state, "final_answer": answer}

    client = _client()
    settings = get_settings()
    context = format_context(state.get("retrieved_chunks", []))
    prompt = (
        f"Question:\n{state['question']}\n\n"
        f"Analysis summary:\n{state.get('analysis_summary', '')}\n\n"
        f"Evidence:\n{context}"
    )
    response = client.responses.create(
        model=settings.openai_chat_model,
        input=[
            {"role": "system", "content": REPORT_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return {**state, "final_answer": response.output_text.strip()}