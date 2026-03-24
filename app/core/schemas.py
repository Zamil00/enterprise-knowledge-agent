from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "enterprise-knowledge-agent"



class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    message: str
    processing_time_seconds: float | None = None

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Question grounded in uploaded documents")
    top_k: Optional[int] = Field(default=None, ge=1, le=15)


class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: int
    document_id: str
    score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    analysis_summary: str
    evidence_quality: str
    retrieved_chunks: List[RetrievedChunk]
    processing_time_seconds: float | None = None