import json
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.models import DocumentChunk


class VectorStore:
    """PostgreSQL pgvector storage and similarity search manager."""

    def add_chunk(
        self,
        db: Session,
        content: str,
        embedding: List[float],
        document_id: Optional[str] = None,
        chunk_index: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DocumentChunk:
        """Persist a single document chunk with vector embedding to PostgreSQL."""
        chunk = DocumentChunk(
            content=content,
            embedding=embedding,
            chunk_metadata=json.dumps(metadata) if metadata else None,
            document_id=document_id,
            chunk_index=chunk_index,
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    def search_similar(
        self,
        db: Session,
        query_embedding: List[float],
        search_type: str = "cosine",
        top_k: int = 5,
        threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform vector distance search over stored chunks."""
        if search_type == "cosine":
            similarity_func = "1 - (embedding <=> CAST(:embedding AS vector))"
            order = "DESC"
        elif search_type == "l2":
            similarity_func = "(embedding <-> CAST(:embedding AS vector))"
            order = "ASC"
        elif search_type == "inner_product":
            similarity_func = "(embedding <#> CAST(:embedding AS vector)) * -1"
            order = "DESC"
        else:
            raise ValueError(f"Unsupported search_type: {search_type}")

        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        query_sql = f"""
            SELECT
                id,
                content,
                chunk_metadata,
                document_id,
                chunk_index,
                created_at,
                {similarity_func} AS similarity
            FROM document_chunks
            WHERE embedding IS NOT NULL
        """
        params: Dict[str, Any] = {"embedding": embedding_str, "top_k": top_k}

        if threshold is not None:
            if search_type == "l2":
                query_sql += f" AND ({similarity_func}) <= :threshold"
            else:
                query_sql += f" AND ({similarity_func}) >= :threshold"
            params["threshold"] = threshold

        query_sql += f" ORDER BY {similarity_func} {order} LIMIT :top_k"

        rows = db.execute(text(query_sql), params).fetchall()
        chunks: List[Dict[str, Any]] = []

        for row in rows:
            meta_raw = row.chunk_metadata
            if metadata_filter:
                try:
                    meta_dict = json.loads(meta_raw) if meta_raw else {}
                    if not all(meta_dict.get(k) == v for k, v in metadata_filter.items()):
                        continue
                except json.JSONDecodeError:
                    continue

            chunks.append({
                "id": row.id,
                "content": row.content,
                "metadata": meta_raw,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "similarity": float(row.similarity),
            })

        return chunks


vector_store = VectorStore()
