"""Database schema initialization and extension provisioning script."""
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from sqlalchemy import text
from src.database import engine, Base, SessionLocal
from src.models import DocumentChunk
from src.services.rag import rag_service


SAMPLE_CORPUS = [
    {
        "content": "Python is a high-level, general-purpose programming language emphasizing code readability and simplicity. It powers major data engineering, web development, and artificial intelligence systems.",
        "document_id": "overview_python",
        "chunk_index": 0,
        "metadata": {"category": "programming", "topic": "python"}
    },
    {
        "content": "FastAPI is a modern, high-performance web framework for building REST APIs with Python 3.8+ using standard Python type hints. It automatically generates interactive OpenAPI/Swagger documentation.",
        "document_id": "overview_fastapi",
        "chunk_index": 0,
        "metadata": {"category": "frameworks", "topic": "fastapi"}
    },
    {
        "content": "PostgreSQL is an advanced open-source object-relational database. The pgvector extension adds native support for vector similarity search using exact distance and HNSW/IVFFlat index structures.",
        "document_id": "overview_pgvector",
        "chunk_index": 0,
        "metadata": {"category": "databases", "topic": "pgvector"}
    },
    {
        "content": "Retrieval-Augmented Generation (RAG) is an architectural pattern that retrieves relevant external knowledge chunks via vector search and injects them into an LLM's prompt context to reduce hallucinations.",
        "document_id": "overview_rag",
        "chunk_index": 0,
        "metadata": {"category": "ai", "topic": "rag"}
    },
    {
        "content": "Dense vector embeddings represent text semantics in continuous high-dimensional space. Cosine distance measures angular similarity, while L2 distance computes Euclidean distance between embeddings.",
        "document_id": "overview_embeddings",
        "chunk_index": 0,
        "metadata": {"category": "ai", "topic": "embeddings"}
    }
]


def init_database():
    print("Provisioning PostgreSQL vector extension...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Database schema initialized successfully.")


def seed_sample_data():
    print("\nSeeding foundational knowledge corpus...")
    db = SessionLocal()
    try:
        # Check if already seeded
        existing_count = db.query(DocumentChunk).count()
        if existing_count > 0:
            print(f"[SKIP] Database already contains {existing_count} chunk(s). Use --reset to re-seed.")
            return

        for doc in SAMPLE_CORPUS:
            rag_service.add_document(
                db=db,
                content=doc["content"],
                document_id=doc["document_id"],
                chunk_index=doc["chunk_index"],
                metadata=doc["metadata"],
            )
            print(f"  + Ingested chunk: {doc['document_id']}")

        print(f"[OK] Ingested {len(SAMPLE_CORPUS)} sample knowledge chunks.")
    finally:
        db.close()


def reset_data():
    print("Resetting document_chunks table...")
    db = SessionLocal()
    try:
        db.query(DocumentChunk).delete()
        db.commit()
        print("[OK] Cleared all document chunks.")
    finally:
        db.close()


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_data()
    init_database()
    if "--no-seed" not in sys.argv:
        seed_sample_data()
    print("\nDatabase initialization complete.")
