from typing import Any, Dict, List
from app.services.embeddings import embed_texts
from app.services.vector_store import search_chunks


def retrieve(question: str, top_k: int, document_id: str) -> List[Dict[str, Any]]:
    query_embedding = embed_texts([question])[0]
    return search_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
        document_id=document_id,
    )