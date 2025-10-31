"""Main FastAPI application."""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.database import get_db, engine, Base
from src.services import rag_service
from src.config import settings

# Create database tables (only if database is available)
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # Database not available yet, will be created on first request
    pass

app = FastAPI(
    title="RAG Engine API",
    description="Custom Retrieval Augmented Generation API with PostgreSQL and Gemini",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., description="The search query")
    search_type: str = Field(
        default="cosine",
        description="Type of similarity search: 'cosine', 'l2', or 'inner_product'"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of results to return"
    )
    threshold: Optional[float] = Field(
        default=None,
        description="Minimum similarity threshold (optional)"
    )
    metadata_filter: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata filters"
    )


class ChunkResponse(BaseModel):
    """Response model for a single chunk."""
    id: int
    content: str
    metadata: Optional[str]
    document_id: Optional[str]
    chunk_index: Optional[int]
    similarity: float


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    query: str
    chunks: List[ChunkResponse]
    search_type: str
    top_k: int


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rag-engine"}


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query the RAG engine with custom parameters.
    
    Returns relevant document chunks based on the query and search parameters.
    """
    try:
        # Generate embedding for query
        query_embedding = rag_service.generate_embedding(request.query, task_type="RETRIEVAL_QUERY")
        
        # Perform similarity search
        chunks = rag_service.similarity_search(
            db=db,
            query_embedding=query_embedding,
            search_type=request.search_type,
            top_k=request.top_k,
            threshold=request.threshold,
            metadata_filter=request.metadata_filter
        )
        
        # Format response
        chunk_responses = [
            ChunkResponse(
                id=chunk["id"],
                content=chunk["content"],
                metadata=chunk["metadata"],
                document_id=chunk["document_id"],
                chunk_index=chunk["chunk_index"],
                similarity=chunk["similarity"]
            )
            for chunk in chunks
        ]
        
        return QueryResponse(
            query=request.query,
            chunks=chunk_responses,
            search_type=request.search_type,
            top_k=len(chunk_responses)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

