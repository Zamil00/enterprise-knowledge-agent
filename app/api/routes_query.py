import logging
import time

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.core.schemas import QueryRequest, QueryResponse, RetrievedChunk
from app.services.graph import build_graph

router = APIRouter(prefix="/query", tags=["query"])
logger = logging.getLogger(__name__)
compiled_graph = build_graph()


@router.post("", response_model=QueryResponse)
def query_documents(payload: QueryRequest) -> QueryResponse:
    start_time = time.perf_counter()
    settings = get_settings()

    initial_state = {
        "question": payload.question,
        "top_k": payload.top_k or settings.top_k_results,
    }

    try:
        result = compiled_graph.invoke(initial_state)
    except Exception as exc:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail="Query processing failed") from exc

    processing_time_seconds = round(time.perf_counter() - start_time, 3)
    logger.info(
        "Query completed | question=%s | evidence_quality=%s | chunks=%s | time=%.3fs",
        payload.question,
        result.get("evidence_quality", "unknown"),
        len(result.get("retrieved_chunks", [])),
        processing_time_seconds,
    )

    chunks = [RetrievedChunk(**chunk) for chunk in result.get("retrieved_chunks", [])]

    return QueryResponse(
        answer=result.get("final_answer", "No answer produced."),
        analysis_summary=result.get("analysis_summary", "No analysis produced."),
        evidence_quality=result.get("evidence_quality", "unknown"),
        retrieved_chunks=chunks,
        processing_time_seconds=processing_time_seconds,
    )