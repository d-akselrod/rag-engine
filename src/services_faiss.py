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
        # Use the latest Gemini Flash model available
        # Try newer models first, fallback to older ones
        try:
            self.chat_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.model_name = "gemini-2.0-flash-exp"
        except:
            try:
                self.chat_model = genai.GenerativeModel('gemini-2.0-flash')
                self.model_name = "gemini-2.0-flash"
            except:
                try:
                    self.chat_model = genai.GenerativeModel('gemini-1.5-flash')
                    self.model_name = "gemini-1.5-flash"
                except:
                    self.chat_model = genai.GenerativeModel('models/gemini-pro')
                    self.model_name = "gemini-pro"
    
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
        conversation_history: Optional[List[Dict[str, str]]] = None,
        search_type: str = "cosine",
        top_k: int = 3,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with RAG context using Gemini Flash with conversation history.
        
        Args:
            user_message: User's message/query
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            search_type: Type of similarity search
            top_k: Number of relevant chunks to retrieve
            temperature: LLM temperature (0.0-1.0)
            system_prompt: Optional custom system prompt
        
        Returns:
            Dictionary with response and context information
        """
        # Step 1: Retrieve relevant context using RAG
        # Use the entire conversation context for better retrieval
        query_for_retrieval = user_message
        if conversation_history:
            # Combine recent conversation with current message for better context
            recent_context = " ".join([
                msg.get("content", "") for msg in conversation_history[-3:]
                if msg.get("role") == "user"
            ])
            if recent_context:
                query_for_retrieval = f"{recent_context} {user_message}"
        
        query_embedding = self.generate_embedding(
            query_for_retrieval, 
            task_type="RETRIEVAL_QUERY"
        )
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
        
        # Step 3: Build the prompt with RAG context and conversation history
        default_system_prompt = """You are a helpful AI assistant with access to relevant context from a knowledge base. 
Use the provided context to answer questions accurately. Maintain conversation context and provide natural, 
conversational responses. If the context doesn't contain enough information, say so and provide the best 
answer you can based on your general knowledge."""
        
        system_prompt = system_prompt or default_system_prompt
        
        # Build conversation history string
        history_text = ""
        if conversation_history:
            history_parts = []
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    history_parts.append(f"User: {content}")
                else:
                    history_parts.append(f"Assistant: {content}")
            history_text = "\n".join(history_parts)
        
        # Step 4: Construct full prompt with history and context
        if context_text:
            if history_text:
                full_prompt = f"""{system_prompt}

Previous Conversation:
{history_text}

Relevant Context from Knowledge Base:
{context_text}

Current User Question: {user_message}

Please provide a helpful and accurate response based on the context and conversation history above. Maintain conversational flow."""
            else:
                full_prompt = f"""{system_prompt}

Relevant Context from Knowledge Base:
{context_text}

User Question: {user_message}

Please provide a helpful and accurate response based on the context above."""
        else:
            if history_text:
                full_prompt = f"""{system_prompt}

Previous Conversation:
{history_text}

Current User Question: {user_message}

Note: No relevant context was found in the knowledge base. Please provide a helpful response based on your general knowledge and the conversation history."""
            else:
                full_prompt = f"""{system_prompt}

User Question: {user_message}

Note: No relevant context was found in the knowledge base. Please provide a helpful response based on your general knowledge."""
        
        # Step 5: Generate response using Gemini Flash
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
                "model": self.model_name
            }
        except Exception as e:
            return {
                "response": f"Error generating response: {str(e)}",
                "user_message": user_message,
                "context_used": len(relevant_chunks),
                "context_chunks": [],
                "model": self.model_name,
                "error": str(e)
            }


rag_service = RAGService()

