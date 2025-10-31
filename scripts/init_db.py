"""Script to initialize database and add sample data."""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from sqlalchemy import create_engine, text
from src.config import settings
from src.database import Base, engine
from src.models import DocumentChunk
from src.services import rag_service

def init_database():
    """Initialize database with pgvector extension."""
    print("Initializing database...")
    
    # Create connection
    conn = engine.connect()
    
    try:
        # Enable pgvector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        print("[OK] pgvector extension enabled")
    except Exception as e:
        print(f"[WARNING] Could not enable pgvector extension: {e}")
        print("The database will work but vector search won't function.")
        print("To install pgvector, download from: https://github.com/pgvector/pgvector/releases")
    
    conn.close()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def add_sample_data():
    """Add sample document chunks to the database."""
    print("\nAdding sample data...")
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    sample_chunks = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and artificial intelligence.",
            "document_id": "doc1",
            "chunk_index": 0,
            "metadata": '{"topic": "programming", "language": "python"}'
        },
        {
            "content": "FastAPI is a modern web framework for building APIs with Python. It's fast, easy to use, and provides automatic API documentation.",
            "document_id": "doc1",
            "chunk_index": 1,
            "metadata": '{"topic": "web development", "framework": "fastapi"}'
        },
        {
            "content": "PostgreSQL is a powerful open-source relational database system. The pgvector extension adds vector similarity search capabilities.",
            "document_id": "doc2",
            "chunk_index": 0,
            "metadata": '{"topic": "databases", "type": "relational"}'
        },
        {
            "content": "Retrieval Augmented Generation (RAG) combines information retrieval with generative AI to provide more accurate and contextual responses.",
            "document_id": "doc3",
            "chunk_index": 0,
            "metadata": '{"topic": "AI", "technique": "RAG"}'
        },
        {
            "content": "Vector embeddings are numerical representations of text that capture semantic meaning. Similar texts have similar embeddings.",
            "document_id": "doc3",
            "chunk_index": 1,
            "metadata": '{"topic": "AI", "concept": "embeddings"}'
        }
    ]
    
    try:
        for chunk_data in sample_chunks:
            # Generate embedding
            embedding = rag_service.generate_embedding(
                chunk_data["content"],
                task_type="RETRIEVAL_DOCUMENT"
            )
            
            # Create chunk
            chunk = DocumentChunk(
                content=chunk_data["content"],
                embedding=embedding,
                chunk_metadata=chunk_data["metadata"],
                document_id=chunk_data["document_id"],
                chunk_index=chunk_data["chunk_index"]
            )
            
            session.add(chunk)
        
        session.commit()
        print(f"✓ Added {len(sample_chunks)} sample chunks")
    except Exception as e:
        print(f"✗ Error adding sample data: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--skip-data":
        init_database()
    else:
        init_database()
        add_sample_data()
    print("\n✓ Database initialization complete!")

