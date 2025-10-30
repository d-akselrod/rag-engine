import pytest
from pydantic import ValidationError
from src.schemas import (
    QueryRequest,
    AddContentRequest,
    ChatRequest,
    ChatMessage,
)


def test_query_request_defaults():
    req = QueryRequest(query="PostgreSQL vector")
    assert req.query == "PostgreSQL vector"
    assert req.search_type == "cosine"
    assert req.top_k == 5
    assert req.rerank is False


def test_query_request_validation():
    with pytest.raises(ValidationError):
        QueryRequest(query="")


def test_add_content_request_auto_chunk():
    req = AddContentRequest(
        content="Long content here...",
        document_id="doc_123",
        auto_chunk=True,
        chunk_size=500,
        chunk_overlap=50,
    )
    assert req.auto_chunk is True
    assert req.chunk_size == 500


def test_chat_request_with_history():
    req = ChatRequest(
        message="Follow up question",
        conversation_history=[
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi! How can I help?"),
        ],
        top_k=4,
    )
    assert len(req.conversation_history) == 2
    assert req.top_k == 4
