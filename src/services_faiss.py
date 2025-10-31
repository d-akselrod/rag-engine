"""RAG service using FAISS instead of PostgreSQL."""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from src.config import settings
from src.faiss_db import (
    add_chunk,
    search_similar,
    get_info,
    clear_all
)


class RAGService:
    """Service for RAG operations using FAISS."""
    
    def __init__(self):
        """Initialize the RAG service with Gemini API."""
        genai.configure(api_key=settings.gemini_api_key)
        self.chat_model = genai.GenerativeModel('gemini-1.5-flash')
    
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
    ) -> int:
        """Add a document chunk to the vector database."""
        # Generate embedding
        embedding = self.generate_embedding(content, task_type="RETRIEVAL_DOCUMENT")
        
        # Add to FAISS
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
        return get_info()
    
    def chat_with_rag(
        self,
        user_message: str,
        search_type: str = "cosine",
        top_k: int = 3,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with RAG context using Gemini Flash.
        
        Args:
            user_message: User's message/query
            search_type: Type of similarity search
            top_k: Number of relevant chunks to retrieve
            temperature: LLM temperature (0.0-1.0)
            system_prompt: Optional custom system prompt
        
        Returns:
            Dictionary with response and context information
        """
        # Step 1: Retrieve relevant context using RAG
        query_embedding = self.generate_embedding(user_message, task_type="RETRIEVAL_QUERY")
        relevant_chunks = search_similar(
            query_embedding=query_embedding,
            search_type=search_type,
            top_k=top_k
        )
        
        # Step 2: Format context for the LLM
        context_text = ""
        if relevant_chunks:
            context_parts = []
            for i, chunk in enumerate(relevant_chunks, 1):
                context_parts.append(f"[Context {i}] {chunk['content']}")
            context_text = "\n\n".join(context_parts)
        
        # Step 3: Build the prompt with RAG context
        default_system_prompt = """You are a helpful AI assistant with access to relevant context from a knowledge base. 
Use the provided context to answer questions accurately. If the context doesn't contain enough information, 
say so and provide the best answer you can based on your general knowledge."""
        
        system_prompt = system_prompt or default_system_prompt
        
        if context_text:
            full_prompt = f"""{system_prompt}

Relevant Context from Knowledge Base:
{context_text}

User Question: {user_message}

Please provide a helpful and accurate response based on the context above."""
        else:
            full_prompt = f"""{system_prompt}

User Question: {user_message}

Note: No relevant context was found in the knowledge base. Please provide a helpful response based on your general knowledge."""
        
        # Step 4: Generate response using Gemini Flash
        try:
            response = self.chat_model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': 1024,
                }
            )
            
            answer = response.text
            
            return {
                "response": answer,
                "user_message": user_message,
                "context_used": len(relevant_chunks),
                "context_chunks": [
                    {
                        "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                        "similarity": chunk["similarity"]
                    }
                    for chunk in relevant_chunks
                ],
                "model": "gemini-1.5-flash"
            }
        except Exception as e:
            return {
                "response": f"Error generating response: {str(e)}",
                "user_message": user_message,
                "context_used": len(relevant_chunks),
                "context_chunks": [],
                "model": "gemini-1.5-flash",
                "error": str(e)
            }


rag_service = RAGService()

