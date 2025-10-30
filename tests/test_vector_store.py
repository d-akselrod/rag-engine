import pytest
import numpy as np
from src.database import SessionLocal
from src.services.vector_store import vector_store


def test_vector_search_cosine():
    db = SessionLocal()
    try:
        # Dummy vector of 3072 dims
        query_v = np.zeros(3072, dtype=np.float32)
        query_v[0] = 1.0

        results = vector_store.search_similar(
            db=db,
            query_embedding=query_v.tolist(),
            search_type="cosine",
            top_k=2,
        )
        assert isinstance(results, list)
        if results:
            assert "similarity" in results[0]
            assert "content" in results[0]
            assert "id" in results[0]
    finally:
        db.close()


def test_vector_search_unsupported_type():
    db = SessionLocal()
    try:
        query_v = np.zeros(3072, dtype=np.float32)
        with pytest.raises(ValueError):
            vector_store.search_similar(
                db=db,
                query_embedding=query_v.tolist(),
                search_type="invalid_metric",
            )
    finally:
        db.close()
