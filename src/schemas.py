from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str
    embedding_model: str
    chat_model: str


class ChunkDetail(BaseModel):
    id: int
    content: str
    similarity: float
    document_id: Optional[str] = None
    chunk_index: Optional[int] = None
    metadata: Optional[str] = None
    created_at: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    search_type: str = Field(
        default="cosine",
        description="Similarity metric: 'cosine', 'l2', or 'inner_product'"
    )
    top_k: int = Field(default=5, ge=1, le=50, description="Max candidate chunks to retrieve")
    threshold: Optional[float] = Field(default=None, description="Minimum similarity score cutoff")
    metadata_filter: Optional[Dict[str, Any]] = Field(default=None, description="Exact-match metadata filters")
    rerank: bool = Field(default=False, description="Apply candidate re-ranking")
    rerank_top_k: Optional[int] = Field(default=None, description="Top results after re-ranking")


class QueryResponse(BaseModel):
    query: str
    chunks: List[ChunkDetail]
    search_type: str
    top_k: int
    total_found: int


class AddContentRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Document content to ingest")
    document_id: Optional[str] = Field(default=None, description="Logical document identifier")
    chunk_index: Optional[int] = Field(default=None, description="Zero-based chunk index")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Structured key-value metadata")
    auto_chunk: bool = Field(default=False, description="Automatically split text into multiple chunks")
    chunk_size: Optional[int] = Field(default=1000, description="Target chunk size in characters if auto_chunk=True")
    chunk_overlap: Optional[int] = Field(default=150, description="Chunk overlap in characters if auto_chunk=True")


class AddContentResponse(BaseModel):
    document_id: Optional[str]
    chunk_ids: List[int]
    total_chunks: int
    message: str


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message text content")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Current user prompt")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Prior conversation turn history"
    )
    search_type: str = Field(default="cosine", description="Similarity search type")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of retrieved chunks for context")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="LLM sampling temperature")
    rerank: bool = Field(default=False, description="Enable candidate re-ranking")
    rerank_top_k: Optional[int] = Field(default=None, description="Top candidates after re-ranking")
    system_prompt: Optional[str] = Field(default=None, description="Custom system instruction override")


class ChatResponse(BaseModel):
    response: str
    user_message: str
    context_used: int
    context_chunks: List[Dict[str, Any]]
    model: str
