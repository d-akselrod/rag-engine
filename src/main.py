from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db, engine, Base
from src.models import DocumentChunk
from src.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    ChunkDetail,
    AddContentRequest,
    AddContentResponse,
    ChatRequest,
    ChatResponse,
)
from src.services.rag import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is ready on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RAG Engine API",
    description="Production-grade Retrieval Augmented Generation API with PostgreSQL, pgvector, and Google Gemini",
    version="1.0.0",
    lifespan=lifespan,
)

static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse(static_dir / "index.html")


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Verify service health and active model configurations."""
    return HealthResponse(
        status="healthy",
        service="rag-engine",
        database="PostgreSQL + pgvector",
        embedding_model=settings.embedding_model,
        chat_model=settings.chat_model,
    )


@app.post("/query", response_model=QueryResponse, tags=["Retrieval"])
async def query_knowledge_base(request: QueryRequest, db: Session = Depends(get_db)):
    """Semantic vector search across document chunks stored in pgvector."""
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
    """Ingest new content into the vector database, with optional automatic chunking."""
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


@app.post("/chat", response_model=ChatResponse, tags=["Generation"])
async def chat_with_rag(request: ChatRequest, db: Session = Depends(get_db)):
    """Conversational RAG: retrieves relevant chunks, synthesizes context, and returns answer."""
    try:
        history = (
            [{"role": m.role, "content": m.content} for m in request.conversation_history]
            if request.conversation_history
            else None
        )

        result = rag_service.chat(
            db=db,
            user_message=request.message,
            conversation_history=history,
            search_type=request.search_type,
            top_k=request.top_k,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            rerank=request.rerank,
            rerank_top_k=request.rerank_top_k,
        )

        return ChatResponse(
            response=result["response"],
            user_message=result["user_message"],
            context_used=result["context_used"],
            context_chunks=result["context_chunks"],
            model=result["model"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
