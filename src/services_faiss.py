import google.generativeai as genai
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from src.config import settings
from src.faiss_db import (
    add_chunk,
    search_similar,
    get_info,
    clear_all
)


class RAGService:
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
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
        embedding = self.generate_embedding(content, task_type="RETRIEVAL_DOCUMENT")
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
        metadata_filter: Optional[Dict[str, Any]] = None,
        rerank: bool = False,
        query_text: Optional[str] = None,
        rerank_top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        chunks = search_similar(
            query_embedding=query_embedding,
            search_type=search_type,
            top_k=top_k * 2 if rerank else top_k,
            threshold=threshold,
            metadata_filter=metadata_filter
        )
        
        if rerank and query_text and len(chunks) > 1:
            chunks = self._rerank_chunks(chunks, query_text, rerank_top_k or top_k)
        
        return chunks
    
    def _rerank_chunks(
        self,
        chunks: List[Dict[str, Any]],
        query_text: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        if not chunks or len(chunks) <= 1:
            return chunks[:top_k]
        
        query_embedding = self.generate_embedding(query_text, task_type="RETRIEVAL_QUERY")
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        chunk_embeddings = []
        valid_chunks = []
        
        for chunk in chunks:
            chunk_content = chunk.get("content", "")
            if not chunk_content:
                continue
            
            chunk_embedding = self.generate_embedding(chunk_content, task_type="RETRIEVAL_DOCUMENT")
            chunk_array = np.array([chunk_embedding], dtype=np.float32)
            faiss.normalize_L2(chunk_array)
            
            similarity = float(np.dot(query_array[0], chunk_array[0]))
            
            valid_chunks.append({
                **chunk,
                "similarity": similarity
            })
        
        valid_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return valid_chunks[:top_k]
    
    def get_info(self) -> Dict[str, Any]:
        return get_info()
    
    def chat_with_rag(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        search_type: str = "cosine",
        top_k: int = 3,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        rerank: bool = False,
        rerank_top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        query_for_retrieval = user_message
        if conversation_history:
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
        relevant_chunks = self.similarity_search(
            query_embedding=query_embedding,
            search_type=search_type,
            top_k=top_k,
            rerank=rerank,
            query_text=user_message,
            rerank_top_k=rerank_top_k or top_k
        )
        
        context_text = ""
        if relevant_chunks:
            context_parts = []
            for i, chunk in enumerate(relevant_chunks, 1):
                context_parts.append(f"[Context {i}] {chunk['content']}")
            context_text = "\n\n".join(context_parts)
        
        default_system_prompt = """You are a helpful AI assistant with access to relevant context from a knowledge base. 
Use the provided context to answer questions accurately. Maintain conversation context and provide natural, 
conversational responses. If the context doesn't contain enough information, say so and provide the best 
answer you can based on your general knowledge."""
        
        system_prompt = system_prompt or default_system_prompt
        
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

