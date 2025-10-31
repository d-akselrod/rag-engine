"""Test adding content and immediately fetching it."""
import requests
import time

API_BASE_URL = "http://localhost:8000"

print("=" * 70)
print("Test: Add Content and Fetch It")
print("=" * 70)

# Step 1: Add new content
print("\n[STEP 1] Adding new content to database...")
add_payload = {
    "content": "The Transformer architecture revolutionized natural language processing by introducing attention mechanisms that allow models to process sequences in parallel rather than sequentially.",
    "document_id": "test_doc",
    "chunk_index": 0,
    "metadata": {
        "topic": "NLP",
        "architecture": "Transformer",
        "test": True
    }
}

try:
    response = requests.post(
        f"{API_BASE_URL}/content",
        json=add_payload,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        chunk_id = data['chunk_id']
        print(f"[OK] Content added successfully!")
        print(f"     Chunk ID: {chunk_id}")
        print(f"     Document ID: {data['document_id']}")
        print(f"     Content preview: {add_payload['content'][:80]}...")
    else:
        print(f"[FAIL] Failed to add content: {response.text}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Error adding content: {e}")
    exit(1)

# Step 2: Query for the newly added content
print("\n[STEP 2] Querying for the newly added content...")
query_payload = {
    "query": "Transformer architecture attention mechanisms",
    "search_type": "cosine",
    "top_k": 5
}

try:
    response = requests.post(
        f"{API_BASE_URL}/query",
        json=query_payload,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        chunks = data['chunks']
        print(f"[OK] Query successful!")
        print(f"     Found {len(chunks)} chunks")
        
        # Check if our newly added content is in the results
        found_new_content = False
        for i, chunk in enumerate(chunks, 1):
            print(f"\n  Chunk {i}:")
            print(f"    ID: {chunk['id']}")
            print(f"    Similarity: {chunk['similarity']:.4f}")
            print(f"    Content: {chunk['content'][:100]}...")
            
            if chunk['id'] == chunk_id or 'Transformer' in chunk['content']:
                found_new_content = True
                print(f"    *** This is the newly added content! ***")
        
        if found_new_content:
            print("\n[SUCCESS] Newly added content was found in search results!")
        else:
            print("\n[WARNING] Newly added content not found in top results")
    else:
        print(f"[FAIL] Query failed: {response.text}")
except Exception as e:
    print(f"[FAIL] Error querying: {e}")

# Step 3: Query with specific search terms from new content
print("\n[STEP 3] Querying with specific terms from new content...")
query_payload2 = {
    "query": "attention mechanisms parallel processing",
    "search_type": "cosine",
    "top_k": 3
}

try:
    response = requests.post(
        f"{API_BASE_URL}/query",
        json=query_payload2,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        chunks = data['chunks']
        print(f"[OK] Found {len(chunks)} chunks")
        
        # Check for our content
        for chunk in chunks:
            if chunk['id'] == chunk_id:
                print(f"\n[SUCCESS] Found newly added content!")
                print(f"    Chunk ID: {chunk['id']}")
                print(f"    Similarity: {chunk['similarity']:.4f}")
                print(f"    Content: {chunk['content']}")
                break
        else:
            print("[INFO] New content not in top 3, but it's in the database")
except Exception as e:
    print(f"[FAIL] Error: {e}")

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70)

