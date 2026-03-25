from typing import Any, Dict, List, Optional
import chromadb
from app.config import get_settings


def get_collection():
    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(document_id: str, filename: str, chunks: List[str], embeddings: List[List[float]]) -> int:
    collection = get_collection()
    ids = [f"{document_id}-{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "source": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(ids)


def search_chunks(
    query_embedding: List[float],
    top_k: int = 5,
    document_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    collection = get_collection()

    query_kwargs: Dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }

    if document_id:
        query_kwargs["where"] = {"document_id": document_id}

    results = collection.query(**query_kwargs)

    chunks: List[Dict[str, Any]] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, dists):
        chunks.append(
            {
                "text": doc,
                "source": meta.get("source", "unknown"),
                "chunk_index": int(meta.get("chunk_index", -1)),
                "document_id": meta.get("document_id", "unknown"),
                "score": round(1 - float(dist), 4) if dist is not None else None,
            }
        )

    return chunks