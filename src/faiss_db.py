"""FAISS-based vector storage - simple and efficient."""
import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import os

# Storage directory
FAISS_DB_PATH = Path("faiss_db")
FAISS_DB_PATH.mkdir(exist_ok=True)

INDEX_FILE = FAISS_DB_PATH / "index.faiss"
METADATA_FILE = FAISS_DB_PATH / "metadata.pkl"

# Vector dimension (Gemini text-embedding-004 uses 768)
VECTOR_DIM = 768

# Initialize FAISS index
def get_index():
    """Get or create FAISS index."""
    if INDEX_FILE.exists():
        index = faiss.read_index(str(INDEX_FILE))
    else:
        # Use inner product for cosine similarity (after normalization)
        # We'll normalize vectors for cosine similarity
        index = faiss.IndexFlatIP(VECTOR_DIM)  # Inner product for normalized vectors
    return index

# Load metadata
def load_metadata():
    """Load metadata from disk."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'rb') as f:
            return pickle.load(f)
    return []

# Save metadata
def save_metadata(metadata):
    """Save metadata to disk."""
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(metadata, f)

# Global index and metadata
_index = None
_metadata = []

def get_index_singleton():
    """Get singleton index instance."""
    global _index, _metadata
    if _index is None:
        _index = get_index()
        _metadata = load_metadata()
    return _index, _metadata

def add_chunk(
    content: str,
    embedding: List[float],
    document_id: Optional[str] = None,
    chunk_index: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """Add a document chunk to FAISS."""
    index, meta = get_index_singleton()
    
    # Convert embedding to numpy array
    emb_array = np.array([embedding], dtype=np.float32)
    
    # Normalize for cosine similarity (store normalized vectors)
    faiss.normalize_L2(emb_array)
    
    # Add to index
    chunk_id = index.ntotal
    index.add(emb_array)
    
    # Store metadata
    meta.append({
        "id": chunk_id,
        "content": content,
        "document_id": document_id,
        "chunk_index": chunk_index,
        "metadata": metadata or {}
    })
    
    # Save to disk
    faiss.write_index(index, str(INDEX_FILE))
    save_metadata(meta)
    
    return chunk_id

def search_similar(
    query_embedding: List[float],
    search_type: str = "cosine",
    top_k: int = 5,
    threshold: Optional[float] = None,
    metadata_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks using FAISS.
    
    Args:
        query_embedding: Query embedding vector
        search_type: Type of similarity search ('cosine', 'l2', 'inner_product')
        top_k: Number of results to return
        threshold: Minimum similarity threshold (optional)
        metadata_filter: Optional metadata filters
    
    Returns:
        List of matching chunks with similarity scores
    """
    index, meta = get_index_singleton()
    
    if index.ntotal == 0:
        return []
    
    # Convert query to numpy array
    query_array = np.array([query_embedding], dtype=np.float32)
    
    # Normalize query vector for cosine similarity
    faiss.normalize_L2(query_array)
    
    # Search
    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_array, k)
    
    # Format results
    chunks = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx == -1:  # FAISS returns -1 for invalid results
            continue
        
        chunk_meta = meta[int(idx)]
        
        # Calculate similarity based on search type
        if search_type == "cosine":
            # For normalized vectors, inner product = cosine similarity
            similarity = float(dist)  # Already cosine similarity (inner product of normalized vectors)
        elif search_type == "l2":
            # Need to recompute L2 distance from original vectors
            # For simplicity, convert inner product to approximate L2
            similarity = 1 / (1 + (2 - 2 * dist))  # Approximate conversion
        else:  # inner_product
            similarity = float(dist)  # Already inner product
        
        # Apply threshold filter
        if threshold is not None:
            if search_type == "l2":
                # For L2, lower is better, so we'd need original distances
                # For now, skip threshold check for L2
                pass
            else:
                if similarity < threshold:
                    continue
        
        # Apply metadata filter
        if metadata_filter:
            chunk_meta_dict = chunk_meta.get("metadata", {})
            if not all(chunk_meta_dict.get(k) == v for k, v in metadata_filter.items()):
                continue
        
        chunks.append({
            "id": chunk_meta["id"],
            "content": chunk_meta["content"],
            "metadata": json.dumps(chunk_meta.get("metadata", {})),
            "document_id": chunk_meta.get("document_id"),
            "chunk_index": chunk_meta.get("chunk_index"),
            "similarity": float(similarity)
        })
    
    return chunks

def get_info() -> Dict[str, Any]:
    """Get information about the vector database."""
    index, meta = get_index_singleton()
    return {
        "vector_db": "FAISS",
        "total_chunks": index.ntotal,
        "vector_dimension": VECTOR_DIM,
        "storage_path": str(FAISS_DB_PATH.absolute())
    }

def clear_all():
    """Clear all chunks from the database."""
    global _index, _metadata
    _index = faiss.IndexFlatIP(VECTOR_DIM)  # Inner product for normalized vectors
    _metadata = []
    
    if INDEX_FILE.exists():
        INDEX_FILE.unlink()
    if METADATA_FILE.exists():
        METADATA_FILE.unlink()
    
    faiss.write_index(_index, str(INDEX_FILE))
    save_metadata(_metadata)

