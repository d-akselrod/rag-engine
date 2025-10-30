import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.config import settings


@pytest.fixture
def mock_gemini_embedding():
    """Mock Gemini embedding to return deterministic vectors for unit tests."""
    with patch("src.services.embeddings.embedding_service.embed_text") as mock_embed:
        def _dummy_vector(text: str, task_type: str = "RETRIEVAL_DOCUMENT"):
            import numpy as np
            v = np.zeros(settings.embedding_dim, dtype=np.float32)
            v[0] = 1.0
            return v.tolist()

        mock_embed.side_effect = _dummy_vector
        yield mock_embed


@pytest.fixture
def mock_gemini_chat():
    """Mock Gemini chat generation."""
    with patch("src.services.rag.rag_service.chat_model.generate_content") as mock_gen:
        mock_response = MagicMock()
        mock_response.text = "This is an automated test response grounded in the provided context."
        mock_gen.return_value = mock_response
        yield mock_gen


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    with TestClient(app) as test_client:
        yield test_client
