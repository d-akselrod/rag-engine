import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    database_url: str = "postgresql://raguser:ragpass@localhost:5432/ragdb"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Model configuration
    chat_model: str = "gemini-3.8-flash"
    embedding_model: str = "models/gemini-embedding-2"
    embedding_dim: int = 3072

    # RAG defaults
    default_top_k: int = 3
    default_search_type: str = "cosine"
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 150

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
