from typing import List


def chunk_text(text: str, max_chunk_size: int = 800, overlap: int = 120) -> List[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: List[str] = []
    start = 0
    n = len(cleaned)
    while start < n:
        end = min(start + max_chunk_size, n)
        chunk = cleaned[start:end]
        if end < n:
            last_break = max(chunk.rfind(". "), chunk.rfind("; "), chunk.rfind("? "), chunk.rfind("! "))
            if last_break > max_chunk_size // 2:
                end = start + last_break + 1
                chunk = cleaned[start:end]
        chunks.append(chunk.strip())
        if end == n:
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]
