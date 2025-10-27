from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db, engine, Base
from src.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    ChunkDetail,
    AddContentRequest,
    AddContentResponse,
)
from src.services.rag import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RAG Engine API",
    description="Retrieval Augmented Generation API with PostgreSQL pgvector and Gemini",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy",
        service="rag-engine",
        database="PostgreSQL + pgvector",
        embedding_model=settings.embedding_model,
        chat_model=settings.chat_model,
    )


@app.post("/query", response_model=QueryResponse, tags=["Retrieval"])
async def query_knowledge_base(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        chunks = rag_service.retrieve_context(
            db=db,
            query=request.query,
            search_type=request.search_type,
            top_k=request.top_k,
            threshold=request.threshold,
            metadata_filter=request.metadata_filter,
            rerank=request.rerank,
            rerank_top_k=request.rerank_top_k,
        )

        formatted_chunks = [
            ChunkDetail(
                id=c["id"],
                content=c["content"],
                similarity=c["similarity"],
                document_id=c.get("document_id"),
                chunk_index=c.get("chunk_index"),
                metadata=c.get("metadata"),
                created_at=c.get("created_at"),
            )
            for c in chunks
        ]

        return QueryResponse(
            query=request.query,
            chunks=formatted_chunks,
            search_type=request.search_type,
            top_k=request.top_k,
            total_found=len(formatted_chunks),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@app.post("/content", response_model=AddContentResponse, tags=["Ingestion"])
async def add_content(request: AddContentRequest, db: Session = Depends(get_db)):
    try:
        chunk_ids = rag_service.add_document(
            db=db,
            content=request.content,
            document_id=request.document_id,
            chunk_index=request.chunk_index,
            metadata=request.metadata,
            auto_chunk=request.auto_chunk,
            chunk_size=request.chunk_size or settings.default_chunk_size,
            chunk_overlap=request.chunk_overlap or settings.default_chunk_overlap,
        )

        return AddContentResponse(
            document_id=request.document_id,
            chunk_ids=chunk_ids,
            total_chunks=len(chunk_ids),
            message=f"Successfully ingested {len(chunk_ids)} chunk(s).",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
