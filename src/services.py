"""RAG service for embedding generation and retrieval."""
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from src.config import settings


class RAGService:
    """Service for RAG operations."""
    
    def __init__(self):
        """Initialize the RAG service with Gemini API."""
        genai.configure(api_key=settings.gemini_api_key)
    
    def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_QUERY") -> List[float]:
        """Generate embedding for given text using Gemini text-embedding-004.
        
        Args:
            text: Text to embed
            task_type: Either "RETRIEVAL_QUERY" for queries or "RETRIEVAL_DOCUMENT" for documents
        """
        # Use text-embedding-004 model
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type=task_type
        )
        return result['embedding']
    
    def similarity_search(
        self,
        db: Session,
        query_embedding: List[float],
        search_type: str = "cosine",
        top_k: int = 5,
        threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search with customizable parameters.
        
        Args:
            db: Database session
            query_embedding: Query embedding vector
            search_type: Type of similarity search ('cosine', 'l2', 'inner_product')
            top_k: Number of results to return
            threshold: Minimum similarity threshold (optional)
            metadata_filter: Optional metadata filters (not implemented in basic version)
        
        Returns:
            List of matching chunks with similarity scores
        """
        # Convert embedding to PostgreSQL array format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Build similarity function based on search type
        if search_type == "cosine":
            similarity_func = "1 - (embedding <=> :embedding::vector)"
        elif search_type == "l2":
            similarity_func = "(embedding <-> :embedding::vector)"
        elif search_type == "inner_product":
            similarity_func = "(embedding <#> :embedding::vector) * -1"
        else:
            raise ValueError(f"Unknown search type: {search_type}")
        
        # Build query
        query_sql = f"""
            SELECT 
                id,
                content,
                chunk_metadata,
                document_id,
                chunk_index,
                {similarity_func} as similarity
            FROM document_chunks
            WHERE embedding IS NOT NULL
        """
        
        params = {"embedding": embedding_str}
        
        # Add threshold filter if provided
        if threshold is not None:
            if search_type == "l2":
                query_sql += f" AND ({similarity_func}) <= :threshold"
            else:
                query_sql += f" AND ({similarity_func}) >= :threshold"
            params["threshold"] = threshold
        
        # Order by similarity and limit
        if search_type == "l2":
            query_sql += f" ORDER BY {similarity_func} ASC LIMIT :top_k"
        else:
            query_sql += f" ORDER BY {similarity_func} DESC LIMIT :top_k"
        
        params["top_k"] = top_k
        
        # Execute query
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        # Format results
        chunks = []
        for row in rows:
            chunks.append({
                "id": row.id,
                "content": row.content,
                "metadata": row.chunk_metadata,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "similarity": float(row.similarity)
            })
        
        return chunks


rag_service = RAGService()

