"""ChromaDB-based vector storage instead of PostgreSQL."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path

# Persistent client - stores data locally
CHROMA_DB_PATH = Path("chroma_db")
client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

# Create/get collection
collection = client.get_or_create_collection(
    name="document_chunks",
    metadata={"description": "RAG document chunks with embeddings"}
)

def add_chunk(
    content: str,
    embedding: List[float],
    document_id: Optional[str] = None,
    chunk_index: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Add a document chunk to ChromaDB."""
    chunk_metadata = metadata or {}
    if document_id:
        chunk_metadata["document_id"] = document_id
    if chunk_index is not None:
        chunk_metadata["chunk_index"] = chunk_index
    
    # Generate ID
    chunk_id = f"{document_id}_{chunk_index}" if document_id and chunk_index is not None else None
    
    # Add to collection
    collection.add(
        embeddings=[embedding],
        documents=[content],
        metadatas=[chunk_metadata],
        ids=[chunk_id] if chunk_id else None
    )
    
    return chunk_id or "unknown"

def search_similar(
    query_embedding: List[float],
    search_type: str = "cosine",
    top_k: int = 5,
    threshold: Optional[float] = None,
    metadata_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks using ChromaDB.
    
    Args:
        query_embedding: Query embedding vector
        search_type: Type of similarity search ('cosine', 'l2', 'inner_product')
        top_k: Number of results to return
        threshold: Minimum similarity threshold (optional)
        metadata_filter: Optional metadata filters
    
    Returns:
        List of matching chunks with similarity scores
    """
    # ChromaDB uses cosine similarity by default
    # Map our search types to ChromaDB's distance metrics
    distance_map = {
        "cosine": "cosine",
        "l2": "l2",
        "inner_product": "ip"  # Inner product
    }
    
    distance_metric = distance_map.get(search_type, "cosine")
    
    # Build where clause for metadata filter
    where_clause = None
    if metadata_filter:
        where_clause = metadata_filter
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause
    )
    
    # Format results
    chunks = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i, (doc_id, doc, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0] if 'distances' in results else [0.0] * len(results['ids'][0])
        )):
            # Convert distance to similarity (ChromaDB returns distances)
            if search_type == "cosine":
                similarity = 1 - distance  # Cosine distance -> similarity
            elif search_type == "l2":
                similarity = 1 / (1 + distance)  # Normalize L2 distance
            else:  # inner_product
                similarity = -distance  # Negative distance for inner product
            
            # Apply threshold filter if provided
            if threshold is not None:
                if search_type == "l2":
                    if distance > threshold:
                        continue
                else:
                    if similarity < threshold:
                        continue
            
            chunks.append({
                "id": doc_id,
                "content": doc,
                "metadata": str(metadata) if metadata else None,
                "document_id": metadata.get("document_id") if metadata else None,
                "chunk_index": metadata.get("chunk_index") if metadata else None,
                "similarity": float(similarity)
            })
    
    return chunks

def get_collection_info() -> Dict[str, Any]:
    """Get information about the collection."""
    count = collection.count()
    return {
        "collection_name": "document_chunks",
        "total_chunks": count,
        "storage_path": str(CHROMA_DB_PATH.absolute())
    }

def clear_collection():
    """Clear all chunks from the collection."""
    client.delete_collection(name="document_chunks")
    global collection
    collection = client.get_or_create_collection(
        name="document_chunks",
        metadata={"description": "RAG document chunks with embeddings"}
    )

