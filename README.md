# RAG Engine API

A custom Retrieval Augmented Generation API built with FastAPI, **FAISS** (Facebook AI Similarity Search), and Google Gemini text-embedding-004.

## Features

- FastAPI-based REST API
- **FAISS** vector database (pure Python, no external dependencies)
- Google Gemini text-embedding-004 for embeddings
- Customizable search types and parameters (cosine, L2, inner product)
- Returns retrieved chunks for RAG applications
- **No PostgreSQL required** - uses FAISS for vector storage

## Prerequisites

- Python 3.8+
- Google Gemini API key

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
   - Create `.env` file:
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```
   - Edit `.env` with your configuration:
     - `GEMINI_API_KEY`: Your Google Gemini API key

3. **Initialize the database:**
```bash
python scripts/init_db.py
```
This will create the FAISS index and add sample data for testing.

4. **Run the API:**
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## Why FAISS?

- **Pure Python** - No external database server required
- **Lightweight** - Stores data locally in `faiss_db/` directory
- **Fast** - Optimized for similarity search
- **Easy Setup** - Just `pip install faiss-cpu`
- **No Configuration** - Works out of the box

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

### `POST /content`
Add new document content to the vector database.

**Request Body:**
```json
{
  "content": "Your document content here",
  "document_id": "doc1",           // Optional
  "chunk_index": 0,                 // Optional
  "metadata": {                     // Optional
    "topic": "AI",
    "source": "book"
  }
}
```

**Response:**
```json
{
  "chunk_id": 5,
  "content": "Your document content here",
  "document_id": "doc1",
  "chunk_index": 0,
  "message": "Content added successfully"
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
│   ├── init_db.py        # Database initialization script
│   ├── manage_db.py      # Database management script (Docker)
│   └── verify_setup.py   # Setup verification script
├── docker-compose.yml    # Docker Compose configuration for PostgreSQL
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

