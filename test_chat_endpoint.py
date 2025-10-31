"""Test the new /chat endpoint with RAG."""
import requests
import json

API_BASE_URL = "http://localhost:8000"

print("=" * 70)
print("Testing POST /chat Endpoint with RAG")
print("=" * 70)

# Test 1: Chat with a question that should find relevant context
print("\n[TEST 1] Chat with RAG context retrieval...")
payload = {
    "message": "What is Python programming?",
    "search_type": "cosine",
    "top_k": 3,
    "temperature": 0.7
}

try:
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload,
        timeout=60
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n[OK] Chat response received!")
        print(f"\nUser Question: {data['user_message']}")
        print(f"\nAI Response:")
        print("-" * 70)
        print(data['response'])
        print("-" * 70)
        print(f"\nContext Info:")
        print(f"  - Context chunks used: {data['context_used']}")
        print(f"  - Model: {data['model']}")
        if data['context_chunks']:
            print(f"\nRetrieved Context Chunks:")
            for i, chunk in enumerate(data['context_chunks'], 1):
                print(f"  {i}. Similarity: {chunk['similarity']:.4f}")
                print(f"     Content: {chunk['content'][:100]}...")
    else:
        print(f"[FAIL] Error: {response.text}")
except Exception as e:
    print(f"[FAIL] Exception: {e}")

# Test 2: Chat with a question about machine learning
print("\n" + "=" * 70)
print("[TEST 2] Chat about machine learning...")
payload2 = {
    "message": "Explain machine learning in simple terms",
    "search_type": "cosine",
    "top_k": 2,
    "temperature": 0.8
}

try:
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload2,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n[OK] Chat response received!")
        print(f"\nUser Question: {data['user_message']']}")
        print(f"\nAI Response:")
        print("-" * 70)
        print(data['response'])
        print("-" * 70)
        print(f"\nUsed {data['context_used']} context chunks from knowledge base")
    else:
        print(f"[FAIL] Error: {response.text}")
except Exception as e:
    print(f"[FAIL] Exception: {e}")

print("\n" + "=" * 70)
print("Chat Endpoint Test Complete")
print("=" * 70)

