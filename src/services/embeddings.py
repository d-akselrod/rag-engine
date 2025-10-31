import logging
from typing import List
import google.generativeai as genai
from src.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service wrapping Google Gemini embedding models."""

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dim

    def embed_text(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate embedding vector for a single text chunk or query."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as e:
            logger.warning("Embedding with %s failed: %s. Attempting fallback.", self.model_name, e)
            for fallback in ["models/gemini-embedding-001", "models/gemini-embedding-2-preview"]:
                try:
                    result = genai.embed_content(
                        model=fallback,
                        content=text,
                        task_type=task_type,
                    )
                    self.model_name = fallback
                    return result["embedding"]
                except Exception:
                    continue
            raise RuntimeError(f"Failed to generate embedding: {e}") from e

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding optimized for query retrieval."""
        return self.embed_text(query, task_type="RETRIEVAL_QUERY")

    def embed_document(self, document: str) -> List[float]:
        """Generate embedding optimized for stored documents."""
        return self.embed_text(document, task_type="RETRIEVAL_DOCUMENT")


embedding_service = EmbeddingService()
