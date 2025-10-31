"""RAG service using ChromaDB instead of PostgreSQL."""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from src.config import settings
from src.chroma_db import (
    add_chunk,
    search_similar,
    get_collection_info,
    clear_collection
)


class RAGService:
    """Service for RAG operations using ChromaDB."""
    
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
    
    def add_document_chunk(
        self,
        content: str,
        document_id: Optional[str] = None,
        chunk_index: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a document chunk to the vector database."""
        # Generate embedding
        embedding = self.generate_embedding(content, task_type="RETRIEVAL_DOCUMENT")
        
        # Add to ChromaDB
        chunk_id = add_chunk(
            content=content,
            embedding=embedding,
            document_id=document_id,
            chunk_index=chunk_index,
            metadata=metadata
        )
        
        return chunk_id
    
    def similarity_search(
        self,
        query_embedding: List[float],
        search_type: str = "cosine",
        top_k: int = 5,
        threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search with customizable parameters.
        
        Args:
            query_embedding: Query embedding vector
            search_type: Type of similarity search ('cosine', 'l2', 'inner_product')
            top_k: Number of results to return
            threshold: Minimum similarity threshold (optional)
            metadata_filter: Optional metadata filters
        
        Returns:
            List of matching chunks with similarity scores
        """
        return search_similar(
            query_embedding=query_embedding,
            search_type=search_type,
            top_k=top_k,
            threshold=threshold,
            metadata_filter=metadata_filter
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the vector database."""
        return get_collection_info()


rag_service = RAGService()

