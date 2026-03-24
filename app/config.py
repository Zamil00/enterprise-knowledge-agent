from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = "app/data/chroma"
    upload_dir: str = "app/data/uploads"
    log_level: str = "INFO"
    top_k_results: int = 5
    max_chunk_size: int = 800
    chunk_overlap: int = 120
    max_file_size_mb: int = 10
    collection_name: str = "enterprise_knowledge_agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()