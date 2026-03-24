from typing import Dict, List


def format_context(chunks: List[Dict]) -> str:
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(
            f"[{i}] source={chunk['source']} chunk={chunk['chunk_index']} score={chunk.get('score')}\n{chunk['text']}"
        )
    return "\n\n".join(lines)
