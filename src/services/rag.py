import logging
from typing import Any, Dict, List, Optional
import google.generativeai as genai
import numpy as np
from sqlalchemy.orm import Session
from src.config import settings
from src.services.embeddings import embedding_service
from src.services.vector_store import vector_store
from src.utils.chunking import chunk_text

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestration service for ingestion, semantic retrieval, reranking, and generation."""

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.chat_model
        try:
            self.chat_model = genai.GenerativeModel(self.model_name)
        except Exception:
            for fallback in ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-flash-latest"]:
                try:
                    self.chat_model = genai.GenerativeModel(fallback)
                    self.model_name = fallback
                    break
                except Exception:
                    continue

    def add_document(
        self,
        db: Session,
        content: str,
        document_id: Optional[str] = None,
        chunk_index: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_chunk: bool = False,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ) -> List[int]:
        """Ingest text into the knowledge base, optionally chunking beforehand."""
        if auto_chunk and len(content) > chunk_size:
            text_chunks = chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        else:
            text_chunks = [content]

        chunk_ids: List[int] = []
        base_index = chunk_index or 0

        for i, text_chunk in enumerate(text_chunks):
            embedding = embedding_service.embed_document(text_chunk)
            chunk = vector_store.add_chunk(
                db=db,
                content=text_chunk,
                embedding=embedding,
                document_id=document_id,
                chunk_index=base_index + i,
                metadata=metadata,
            )
            chunk_ids.append(chunk.id)

        return chunk_ids

    def retrieve_context(
        self,
        db: Session,
        query: str,
        search_type: str = "cosine",
        top_k: int = 5,
        threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        rerank: bool = False,
        rerank_top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context chunks with optional secondary reranking."""
        query_embedding = embedding_service.embed_query(query)
        candidate_k = top_k * 2 if rerank else top_k

        candidates = vector_store.search_similar(
            db=db,
            query_embedding=query_embedding,
            search_type=search_type,
            top_k=candidate_k,
            threshold=threshold,
            metadata_filter=metadata_filter,
        )

        if rerank and len(candidates) > 1:
            candidates = self._rerank_candidates(
                candidates=candidates,
                query_text=query,
                top_k=rerank_top_k or top_k,
            )

        return candidates[:top_k]

    def _rerank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        query_text: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Re-score candidates using fresh query and candidate document embeddings."""
        query_emb = np.array(embedding_service.embed_query(query_text), dtype=np.float32)
        q_norm = np.linalg.norm(query_emb)
        if q_norm > 0:
            query_emb = query_emb / q_norm

        reranked: List[Dict[str, Any]] = []
        for cand in candidates:
            txt = cand.get("content", "").strip()
            if not txt:
                continue

            doc_emb = np.array(embedding_service.embed_document(txt), dtype=np.float32)
            d_norm = np.linalg.norm(doc_emb)
            if d_norm > 0:
                doc_emb = doc_emb / d_norm

            score = float(np.dot(query_emb, doc_emb))
            reranked.append({**cand, "similarity": score})

        reranked.sort(key=lambda x: x["similarity"], reverse=True)
        return reranked[:top_k]

    def chat(
        self,
        db: Session,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        search_type: str = "cosine",
        top_k: int = 3,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        rerank: bool = False,
        rerank_top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Perform RAG chat: contextual retrieval -> prompt synthesis -> LLM response."""
        # Synthesize retrieval query from user message and recent turn context
        retrieval_query = user_message
        if conversation_history:
            recent_user_turns = [
                m["content"] for m in conversation_history[-3:] if m.get("role") == "user"
            ]
            if recent_user_turns:
                retrieval_query = f"{' '.join(recent_user_turns)} {user_message}"

        context_chunks = self.retrieve_context(
            db=db,
            query=retrieval_query,
            search_type=search_type,
            top_k=top_k,
            rerank=rerank,
            rerank_top_k=rerank_top_k,
        )

        # Assemble prompt
        default_prompt = (
            "You are a helpful knowledge assistant with access to relevant context excerpts from a verified knowledge base. "
            "Use the provided context to answer questions truthfully and precisely. "
            "If the context does not contain the answer, acknowledge the limitation and answer based on general knowledge."
        )
        sys_instruction = system_prompt or default_prompt

        context_block = ""
        if context_chunks:
            items = [f"[Source {i+1}] {c['content']}" for i, c in enumerate(context_chunks)]
            context_block = "\n\n".join(items)

        history_block = ""
        if conversation_history:
            lines = [
                f"{'User' if m.get('role') == 'user' else 'Assistant'}: {m.get('content', '')}"
                for m in conversation_history
            ]
            history_block = "\n".join(lines)

        prompt_parts = [sys_instruction]
        if history_block:
            prompt_parts.append(f"Conversation History:\n{history_block}")
        if context_block:
            prompt_parts.append(f"Context from Knowledge Base:\n{context_block}")
        else:
            prompt_parts.append("Note: No relevant context found in knowledge base.")
        prompt_parts.append(f"User Question: {user_message}\n\nAnswer:")

        full_prompt = "\n\n".join(prompt_parts)

        try:
            response = self.chat_model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 1024,
                },
            )
            answer = response.text
        except Exception as e:
            logger.error("Error generating chat completion: %s", e)
            answer = f"Error generating response: {e}"

        return {
            "response": answer,
            "user_message": user_message,
            "context_used": len(context_chunks),
            "context_chunks": [
                {
                    "content": (c["content"][:240] + "...") if len(c["content"]) > 240 else c["content"],
                    "similarity": round(c["similarity"], 4),
                    "document_id": c.get("document_id"),
                }
                for c in context_chunks
            ],
            "model": self.model_name,
        }


rag_service = RAGService()
