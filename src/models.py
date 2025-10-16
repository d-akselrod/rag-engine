from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from pgvector.sqlalchemy import Vector
from src.database import Base


class DocumentChunk(Base):
    """Model representing a document text chunk with its vector embedding."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(3072), nullable=False)
    chunk_metadata = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    @property
    def metadata_dict(self) -> Dict[str, Any]:
        """Parsed JSON metadata dictionary."""
        if not self.chunk_metadata:
            return {}
        try:
            return json.loads(self.chunk_metadata)
        except json.JSONDecodeError:
            return {}

    def to_dict(self, similarity: Optional[float] = None) -> Dict[str, Any]:
        """Serialize chunk to dictionary."""
        result = {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "metadata": self.chunk_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if similarity is not None:
            result["similarity"] = round(similarity, 4)
        return result
