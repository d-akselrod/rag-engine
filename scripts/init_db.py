import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from src.services_faiss import rag_service
from src.faiss_db import clear_all

def init_database():
    print("Initializing FAISS database...")
    clear_all()
    print("[OK] FAISS database initialized")

def add_sample_data():
    print("\nAdding sample data...")
    
    sample_chunks = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and artificial intelligence.",
            "document_id": "doc1",
            "chunk_index": 0,
            "metadata": {"topic": "programming", "language": "python"}
        },
        {
            "content": "FastAPI is a modern web framework for building APIs with Python. It's fast, easy to use, and provides automatic API documentation.",
            "document_id": "doc1",
            "chunk_index": 1,
            "metadata": {"topic": "web development", "framework": "fastapi"}
        },
        {
            "content": "PostgreSQL is a powerful open-source relational database system. The pgvector extension adds vector similarity search capabilities.",
            "document_id": "doc2",
            "chunk_index": 0,
            "metadata": {"topic": "databases", "type": "relational"}
        },
        {
            "content": "Retrieval Augmented Generation (RAG) combines information retrieval with generative AI to provide more accurate and contextual responses.",
            "document_id": "doc3",
            "chunk_index": 0,
            "metadata": {"topic": "AI", "technique": "RAG"}
        },
        {
            "content": "Vector embeddings are numerical representations of text that capture semantic meaning. Similar texts have similar embeddings.",
            "document_id": "doc3",
            "chunk_index": 1,
            "metadata": {"topic": "AI", "concept": "embeddings"}
        }
    ]
    
    try:
        for chunk_data in sample_chunks:
            chunk_id = rag_service.add_document_chunk(
                content=chunk_data["content"],
                document_id=chunk_data["document_id"],
                chunk_index=chunk_data["chunk_index"],
                metadata=chunk_data["metadata"]
            )
            print(f"  Added chunk: {chunk_id}")
        
        print(f"[OK] Added {len(sample_chunks)} sample chunks")
    except Exception as e:
        print(f"[FAIL] Error adding sample data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--skip-data":
        init_database()
    else:
        init_database()
        add_sample_data()
    print("\n[OK] Database initialization complete!")
    print("\nFAISS stores data locally in: faiss_db/")
    print("You can now start the API: uvicorn src.main:app --reload")
