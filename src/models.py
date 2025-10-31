"""Database models for the RAG engine."""
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from src.database import Base


class DocumentChunk(Base):
    """Model for storing document chunks with embeddings."""
    
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False, index=True)
    embedding = Column(Vector(768), nullable=False)  # Gemini text-embedding-001 uses 768 dimensions
    metadata = Column(Text, nullable=True)  # JSON string for additional metadata
    document_id = Column(String, nullable=True, index=True)
    chunk_index = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id})>"

