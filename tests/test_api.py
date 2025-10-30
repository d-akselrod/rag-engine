import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "rag-engine"
    assert "pgvector" in data["database"]


def test_query_endpoint(client, mock_gemini_embedding):
    response = client.post(
        "/query",
        json={"query": "FastAPI framework", "top_k": 3, "search_type": "cosine"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "chunks" in data
    assert isinstance(data["chunks"], list)


def test_content_ingest(client, mock_gemini_embedding):
    response = client.post(
        "/content",
        json={
            "content": "Pgvector enables fast vector similarity search directly inside SQL.",
            "document_id": "test_ingest",
            "metadata": {"source": "unit_test"},
            "auto_chunk": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_chunks"] == 1
    assert len(data["chunk_ids"]) == 1


def test_content_ingest_auto_chunk(client, mock_gemini_embedding):
    long_content = "Paragraph one with some text. " * 50
    response = client.post(
        "/content",
        json={
            "content": long_content,
            "document_id": "test_chunked",
            "auto_chunk": True,
            "chunk_size": 200,
            "chunk_overlap": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_chunks"] > 1


def test_chat_endpoint(client, mock_gemini_embedding, mock_gemini_chat):
    response = client.post(
        "/chat",
        json={
            "message": "Explain RAG architecture",
            "top_k": 2,
            "temperature": 0.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["context_used"] >= 0
    assert "model" in data
