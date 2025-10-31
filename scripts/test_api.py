"""Comprehensive test script for RAG Engine API."""
import sys
import os
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests")
    import requests

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("[OK] Health check passed")
        return True
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

def test_query_basic():
    """Test basic query endpoint."""
    print("\n=== Testing Query Endpoint (Basic) ===")
    try:
        payload = {
            "query": "What is Python programming language?",
            "search_type": "cosine",
            "top_k": 3
        }
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Found {len(data['chunks'])} chunks")
            for i, chunk in enumerate(data['chunks'], 1):
                print(f"  Chunk {i}: similarity={chunk['similarity']:.4f}")
                print(f"    Content: {chunk['content'][:80]}...")
            print("[OK] Basic query test passed")
            return True
        else:
            print(f"Response: {response.text}")
            print("[FAIL] Basic query test failed")
            return False
    except Exception as e:
        print(f"[FAIL] Basic query test failed: {e}")
        return False

def test_query_l2():
    """Test query with L2 distance."""
    print("\n=== Testing Query Endpoint (L2 Distance) ===")
    try:
        payload = {
            "query": "How does FastAPI work?",
            "search_type": "l2",
            "top_k": 2
        }
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['chunks'])} chunks")
            print("[OK] L2 distance query test passed")
            return True
        else:
            print(f"Response: {response.text}")
            print("[FAIL] L2 distance query test failed")
            return False
    except Exception as e:
        print(f"[FAIL] L2 distance query test failed: {e}")
        return False

def test_query_inner_product():
    """Test query with inner product."""
    print("\n=== Testing Query Endpoint (Inner Product) ===")
    try:
        payload = {
            "query": "Tell me about vector embeddings",
            "search_type": "inner_product",
            "top_k": 5
        }
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['chunks'])} chunks")
            print("[OK] Inner product query test passed")
            return True
        else:
            print(f"Response: {response.text}")
            print("[FAIL] Inner product query test failed")
            return False
    except Exception as e:
        print(f"[FAIL] Inner product query test failed: {e}")
        return False

def test_query_with_threshold():
    """Test query with threshold."""
    print("\n=== Testing Query Endpoint (With Threshold) ===")
    try:
        payload = {
            "query": "database systems",
            "search_type": "cosine",
            "top_k": 10,
            "threshold": 0.5
        }
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['chunks'])} chunks (above threshold)")
            print("[OK] Threshold query test passed")
            return True
        else:
            print(f"Response: {response.text}")
            print("[FAIL] Threshold query test failed")
            return False
    except Exception as e:
        print(f"[FAIL] Threshold query test failed: {e}")
        return False

def check_api_running():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("RAG Engine API - Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if API is running
    print("\n[INFO] Checking if API is running...")
    if not check_api_running():
        print("\n[FAIL] API is not running!")
        print("Please start the API with: uvicorn src.main:app --reload")
        sys.exit(1)
    
    print("[OK] API is running")
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Basic Query", test_query_basic()))
    results.append(("L2 Distance Query", test_query_l2()))
    results.append(("Inner Product Query", test_query_inner_product()))
    results.append(("Threshold Query", test_query_with_threshold()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

