from typing import List
from openai import OpenAI
from app.config import get_settings


def embed_texts(texts: List[str]) -> List[List[float]]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Create a .env file before indexing documents.")
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [item.embedding for item in response.data]
