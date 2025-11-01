import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

FAISS_DB_PATH = Path("faiss_db")
FAISS_DB_PATH.mkdir(exist_ok=True)

INDEX_FILE = FAISS_DB_PATH / "index.faiss"
METADATA_FILE = FAISS_DB_PATH / "metadata.pkl"

VECTOR_DIM = 768

def get_index():
    if INDEX_FILE.exists():
        index = faiss.read_index(str(INDEX_FILE))
    else:
        index = faiss.IndexFlatIP(VECTOR_DIM)
    return index

def load_metadata():
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'rb') as f:
            return pickle.load(f)
    return []

def save_metadata(metadata):
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(metadata, f)

_index = None
_metadata = []

def get_index_singleton():
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
    index, meta = get_index_singleton()
    emb_array = np.array([embedding], dtype=np.float32)
    faiss.normalize_L2(emb_array)
    chunk_id = index.ntotal
    index.add(emb_array)
    meta.append({
        "id": chunk_id,
        "content": content,
        "document_id": document_id,
        "chunk_index": chunk_index,
        "metadata": metadata or {}
    })
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
    index, meta = get_index_singleton()
    
    if index.ntotal == 0:
        return []
    
    query_array = np.array([query_embedding], dtype=np.float32)
    faiss.normalize_L2(query_array)
    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_array, k)
    
    chunks = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx == -1:
            continue
        
        chunk_meta = meta[int(idx)]
        
        if search_type == "cosine":
            similarity = float(dist)
        elif search_type == "l2":
            similarity = 1 / (1 + (2 - 2 * dist))
        else:
            similarity = float(dist)
        
        if threshold is not None:
            if search_type == "l2":
                pass
            else:
                if similarity < threshold:
                    continue
        
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
    index, meta = get_index_singleton()
    return {
        "vector_db": "FAISS",
        "total_chunks": index.ntotal,
        "vector_dimension": VECTOR_DIM,
        "storage_path": str(FAISS_DB_PATH.absolute())
    }

def clear_all():
    global _index, _metadata
    _index = faiss.IndexFlatIP(VECTOR_DIM)
    _metadata = []
    
    if INDEX_FILE.exists():
        INDEX_FILE.unlink()
    if METADATA_FILE.exists():
        METADATA_FILE.unlink()
    
    faiss.write_index(_index, str(INDEX_FILE))
    save_metadata(_metadata)

