# RAG Engine API

A custom Retrieval Augmented Generation API built with FastAPI, PostgreSQL (pgvector), and Google Gemini text-embedding-001.

## Features

- FastAPI-based REST API
- PostgreSQL with pgvector for vector similarity search
- Google Gemini text-embedding-001 for embeddings
- Customizable search types and parameters (cosine, L2, inner product)
- Returns retrieved chunks for RAG applications

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ with pgvector extension installed
- Google Gemini API key

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL:**
   - Install PostgreSQL and the pgvector extension
   - Create a database for the RAG engine:
   ```sql
   CREATE DATABASE ragdb;
   ```
   - Connect to the database and enable pgvector:
   ```sql
   \c ragdb
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` with your configuration:
     - `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/ragdb`)
     - `GEMINI_API_KEY`: Your Google Gemini API key

4. **Initialize the database:**
```bash
python scripts/init_db.py
```
This will create the necessary tables and add sample data for testing.

5. **Run the API:**
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-engine"
}
```

### `POST /query`
Query the RAG engine with custom parameters.

**Request Body:**
```json
{
  "query": "your search query",
  "search_type": "cosine",  // Options: "cosine", "l2", "inner_product"
  "top_k": 5,                // Number of results (1-100)
  "threshold": 0.5,          // Optional: minimum similarity threshold
  "metadata_filter": null    // Optional: metadata filters (not implemented)
}
```

**Response:**
```json
{
  "query": "your search query",
  "chunks": [
    {
      "id": 1,
      "content": "chunk content",
      "metadata": "{\"topic\": \"programming\"}",
      "document_id": "doc1",
      "chunk_index": 0,
      "similarity": 0.85
    }
  ],
  "search_type": "cosine",
  "top_k": 1
}
```

## Testing

Use the provided test scripts:

**Linux/Mac:**
```bash
bash test_api.sh
```

**Windows:**
```bash
test_api.bat
```

Or test manually with curl:

```bash
# Health check
curl -X GET http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "search_type": "cosine",
    "top_k": 3
  }'
```

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
rag-engine/
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── models.py         # SQLAlchemy models
│   └── services.py       # RAG service logic
├── scripts/
│   └── init_db.py        # Database initialization script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── test_api.sh          # Test script (Linux/Mac)
├── test_api.bat         # Test script (Windows)
└── README.md            # This file
```

## Search Types

- **cosine**: Cosine similarity (range: 0-1, higher is better)
- **l2**: Euclidean distance (lower is better)
- **inner_product**: Inner product similarity (higher is better, negated for consistency)

## License

MIT

