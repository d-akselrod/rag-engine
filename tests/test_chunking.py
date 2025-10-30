import pytest
from src.utils.chunking import chunk_text


def test_chunk_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []
    assert chunk_text(None) == []


def test_chunk_short_text():
    text = "Short sentence under maximum size."
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_long_text():
    paragraphs = [
        "First paragraph discussing PostgreSQL and pgvector database capabilities.",
        "Second paragraph covering FastAPI integration and async request lifecycles.",
        "Third paragraph explaining Google Gemini embedding models and retrieval.",
        "Fourth paragraph analyzing reranking strategies and cosine distance calculations.",
    ]
    full_text = "\n\n".join(paragraphs)

    chunks = chunk_text(full_text, chunk_size=120, chunk_overlap=30)
    assert len(chunks) >= 3
    # Check that chunks reconstruct the content
    for p in paragraphs:
        assert any(p[:25] in c for c in chunks)


def test_chunk_overlap():
    text = "WordA WordB WordC WordD WordE WordF WordG WordH WordI WordJ WordK WordL WordM WordN"
    chunks = chunk_text(text, chunk_size=30, chunk_overlap=12)
    assert len(chunks) > 1
    # Check that adjacent chunks share characters
    for i in range(len(chunks) - 1):
        c1 = chunks[i]
        c2 = chunks[i + 1]
        c1_words = set(c1.split())
        c2_words = set(c2.split())
        assert len(c1_words.intersection(c2_words)) > 0
