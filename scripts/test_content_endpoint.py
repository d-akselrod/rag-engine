"""Test script for the new /content endpoint."""
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE_URL = "http://localhost:8000"

def test_add_content():
    """Test adding content."""
    print("\n=== Testing POST /content Endpoint ===")
    
    # Test 1: Simple content
    print("\n[Test 1] Adding simple content...")
    payload = {
        "content": "Deep learning is a branch of machine learning that uses neural networks with multiple layers to learn complex patterns in data.",
        "document_id": "doc5",
        "chunk_index": 0,
        "metadata": {"topic": "AI", "subtopic": "deep learning"}
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/content",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Content added with chunk_id: {data['chunk_id']}")
            print(f"     Document ID: {data['document_id']}")
            print(f"     Message: {data['message']}")
            return True, data['chunk_id']
        else:
            print(f"[FAIL] Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False, None

def test_query_new_content():
    """Test querying the newly added content."""
    print("\n=== Testing Query with New Content ===")
    
    payload = {
        "query": "deep learning neural networks",
        "search_type": "cosine",
        "top_k": 2
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Found {len(data['chunks'])} chunks")
            for i, chunk in enumerate(data['chunks'], 1):
                print(f"  Chunk {i}: similarity={chunk['similarity']:.4f}")
                print(f"    Content: {chunk['content'][:80]}...")
            return True
        else:
            print(f"[FAIL] Error: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False

def main():
    """Run tests."""
    print("=" * 70)
    print("Testing POST /content Endpoint")
    print("=" * 70)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("[FAIL] API is not running")
            return
    except:
        print("[FAIL] API is not accessible")
        return
    
    # Test adding content
    success, chunk_id = test_add_content()
    
    if success:
        # Test querying the new content
        test_query_new_content()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] POST /content endpoint is working!")
        print("=" * 70)

if __name__ == "__main__":
    main()

