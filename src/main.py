from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from src.services_faiss import rag_service
from src.config import settings

app = FastAPI(
    title="RAG Engine API",
    description="Custom Retrieval Augmented Generation API with FAISS and Gemini",
    version="1.0.0"
)

static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/")
    async def root():
        return FileResponse(static_dir / "index.html")


class QueryRequest(BaseModel):
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
    rerank: bool = Field(
        default=False,
        description="Enable reranking for better results"
    )
    rerank_top_k: Optional[int] = Field(
        default=None,
        description="Number of results after reranking (if rerank enabled)"
    )


class ChunkResponse(BaseModel):
    id: Any
    content: str
    metadata: Optional[str]
    document_id: Optional[str]
    chunk_index: Optional[int]
    similarity: float


class QueryResponse(BaseModel):
    query: str
    chunks: List[ChunkResponse]
    search_type: str
    top_k: int


class AddContentRequest(BaseModel):
    content: str = Field(..., description="The document content to add")
    document_id: Optional[str] = Field(
        default=None,
        description="Optional document identifier"
    )
    chunk_index: Optional[int] = Field(
        default=None,
        description="Optional chunk index within the document"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata dictionary"
    )


class AddContentResponse(BaseModel):
    chunk_id: int
    content: str
    document_id: Optional[str]
    chunk_index: Optional[int]
    message: str


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/query")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous conversation messages for context"
    )
    search_type: str = Field(
        default="cosine",
        description="Type of similarity search: 'cosine', 'l2', or 'inner_product'"
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve for context"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM temperature (0.0 = deterministic, 1.0 = creative)"
    )
    rerank: bool = Field(
        default=False,
        description="Enable reranking for better context retrieval"
    )
    rerank_top_k: Optional[int] = Field(
        default=None,
        description="Number of results after reranking (if rerank enabled)"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional custom system prompt"
    )


class ChatResponse(BaseModel):
    response: str
    user_message: str
    context_used: int
    context_chunks: List[Dict[str, Any]]
    model: str


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-engine"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        query_embedding = rag_service.generate_embedding(request.query, task_type="RETRIEVAL_QUERY")
        chunks = rag_service.similarity_search(
            query_embedding=query_embedding,
            search_type=request.search_type,
            top_k=request.top_k,
            threshold=request.threshold,
            metadata_filter=request.metadata_filter,
            rerank=request.rerank,
            query_text=request.query if request.rerank else None,
            rerank_top_k=request.rerank_top_k
        )
        chunk_responses = [
            ChunkResponse(
                id=chunk.get("id", 0),
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


@app.post("/content", response_model=AddContentResponse)
async def add_content(request: AddContentRequest):
    try:
        chunk_id = rag_service.add_document_chunk(
            content=request.content,
            document_id=request.document_id,
            chunk_index=request.chunk_index,
            metadata=request.metadata
        )
        
        return AddContentResponse(
            chunk_id=chunk_id,
            content=request.content,
            document_id=request.document_id,
            chunk_index=request.chunk_index,
            message="Content added successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding content: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        history = None
        if request.conversation_history:
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        result = rag_service.chat_with_rag(
            user_message=request.message,
            conversation_history=history,
            search_type=request.search_type,
            top_k=request.top_k,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            rerank=request.rerank,
            rerank_top_k=request.rerank_top_k
        )
        
        return ChatResponse(
            response=result["response"],
            user_message=result["user_message"],
            context_used=result["context_used"],
            context_chunks=result.get("context_chunks", []),
            model=result["model"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

