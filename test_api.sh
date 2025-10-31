#!/bin/bash
# Test script for RAG Engine API

BASE_URL="http://localhost:8000"

echo "=== Testing RAG Engine API ==="
echo ""

echo "1. Health Check..."
curl -X GET "${BASE_URL}/health" | python -m json.tool
echo ""
echo ""

echo "2. Query with default parameters (cosine similarity)..."
curl -X POST "${BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python programming language?",
    "search_type": "cosine",
    "top_k": 3
  }' | python -m json.tool
echo ""
echo ""

echo "3. Query with L2 distance..."
curl -X POST "${BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does FastAPI work?",
    "search_type": "l2",
    "top_k": 2
  }' | python -m json.tool
echo ""
echo ""

echo "4. Query with inner product..."
curl -X POST "${BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about vector embeddings",
    "search_type": "inner_product",
    "top_k": 5
  }' | python -m json.tool
echo ""
echo ""

echo "5. Query with threshold..."
curl -X POST "${BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database systems",
    "search_type": "cosine",
    "top_k": 10,
    "threshold": 0.5
  }' | python -m json.tool
echo ""
echo ""

echo "=== Testing Complete ==="

