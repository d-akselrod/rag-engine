# RAG Engine

A production-grade Retrieval-Augmented Generation (RAG) backend service and conversational interface built with **FastAPI**, **PostgreSQL** with **pgvector**, and **Google Gemini** (Gemini 3.8 Flash & Gemini Embedding 2).

---

## Architecture Overview

```
                      ┌───────────────────────────────────────┐
                      │    Modern Web UI (Chat & Sources)    │
                      └───────────────────┬───────────────────┘
                                          │ HTTP / JSON
                      ┌───────────────────▼───────────────────┐
                      │              FastAPI API              │
                      │   /health   /query   /content   /chat │
                      └─────────┬───────────────────┬─────────┘
                                │                   │
             pgvector queries   │                   │ Embeddings & LLM
            (Cosine / L2 / IP)  │                   │ Generation
                      ┌─────────▼─────────┐       ┌─▼─────────────────┐
                      │    PostgreSQL     │       │   Google Gemini   │
                      │    + pgvector     │       │  Embedding 2 &    │
                      │ (Docker Compose)  │       │  3.8 Flash        │
                      └───────────────────┘       └───────────────────┘
```

### Key Engineering Features
- **Vector Storage**: Uses PostgreSQL 16 with the native `pgvector` extension for storing 3072-dimensional embeddings.
- **Flexible Similarity Metrics**: Supports Cosine Distance (`<=>`), Euclidean Distance (`<->`), and Inner Product (`<#>`).
- **Recursive Text Chunking**: Automatic document chunking with character overlap preserving paragraph and sentence boundaries.
- **Candidate Re-ranking**: Two-stage retrieval workflow that fetches an expanded candidate pool and re-scores candidates with fresh query embeddings.
- **Multi-turn Memory**: Retains conversation history across turns, synthesizing conversational context into retrieval queries.
- **Offline Test Suite**: Pytest suite with mock fixtures for Gemini API calls to test endpoints without requiring live API tokens.
- **Clean Developer Interface**: Dark-themed chat UI with markdown rendering and collapsible retrieved context inspectors showing similarity percentages.

---

## Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Docker & Docker Compose**
- **Google Gemini API Key** ([Google AI Studio](https://aistudio.google.com/))

### 2. Environment Setup

Clone the repository and prepare your virtual environment:

```bash
git clone https://github.com/d-akselrod/rag-engine.git
cd rag-engine

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your `.env` configuration:

```bash
cp .env.example .env
```

Edit `.env` and set your API key:
```env
DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb
GEMINI_API_KEY=your_gemini_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Start PostgreSQL with pgvector

```bash
make db-up
# or: docker compose up -d
```

### 4. Initialize Database Schema

```bash
make db-init
# or: python scripts/init_db.py
```

This activates the `vector` extension, creates the `document_chunks` table, and seeds initial sample knowledge chunks.

### 5. Run Development Server

```bash
make dev
# or: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive Chat Interface**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
- **System Health Check**: `http://localhost:8000/health`

---

## Makefile Targets

| Target | Description |
|---|---|
| `make dev` | Run FastAPI server with auto-reload |
| `make test` | Execute unit and integration tests with pytest |
| `make db-up` | Start PostgreSQL container with pgvector |
| `make db-down` | Stop PostgreSQL container |
| `make db-init` | Create database tables and vector extension |
| `make db-seed` | Ingest sample documents into vector storage |
| `make clean` | Remove Python bytecode and test cache |

---

## API Reference

### 1. `GET /health`
Returns service status, database backend, and active models.

```bash
curl http://localhost:8000/health
```

### 2. `POST /query`
Performs vector similarity search across indexed document chunks.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vector similarity search",
    "search_type": "cosine",
    "top_k": 3,
    "rerank": true
  }'
```

### 3. `POST /content`
Ingests a document. If `auto_chunk` is enabled, large documents are split into overlapping segments.

```bash
curl -X POST http://localhost:8000/content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "PostgreSQL with pgvector provides performant vector similarity search directly in SQL.",
    "document_id": "pgvector_notes",
    "metadata": {"category": "database"},
    "auto_chunk": true,
    "chunk_size": 1000,
    "chunk_overlap": 150
  }'
```

### 4. `POST /chat`
Conversational RAG endpoint. Retrieves context from pgvector, synthesizes context into the prompt, and generates grounded answers with Gemini.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is pgvector?",
    "conversation_history": [],
    "top_k": 3,
    "search_type": "cosine",
    "rerank": false
  }'
```

---

## Ingesting Custom Documents

To ingest any markdown or text file from the command line:

```bash
python scripts/seed_sample.py --file path/to/document.md --id custom_doc_id
```

---

## Testing

Run the automated test suite:

```bash
make test
# or: pytest tests/ -v
```

The test suite mocks Gemini API endpoints, allowing the full pipeline (chunking, schemas, vector queries, API routing) to be verified offline in milliseconds.

---

## Project Structure

```
rag-engine/
├── docker-compose.yml       # PostgreSQL 16 + pgvector container definition
├── Makefile                 # Common developer targets
├── pyproject.toml           # Project metadata and pytest configuration
├── requirements.txt         # Core production dependencies
├── requirements-dev.txt     # Test and developer tools
├── README.md
├── scripts/
│   ├── __init__.py
│   ├── init_db.py           # Database migration & schema setup
│   ├── seed_sample.py       # CLI file/corpus ingestion utility
│   └── verify_setup.py      # Diagnostic environment checks
├── src/
│   ├── __init__.py
│   ├── config.py            # Typed settings via pydantic-settings
│   ├── database.py          # SQLAlchemy engine and session dependency
│   ├── models.py            # DocumentChunk model with pgvector Vector(3072)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embeddings.py    # Gemini Embedding 2 service
│   │   ├── vector_store.py  # pgvector similarity search & CRUD
│   │   └── rag.py           # End-to-end RAG orchestrator & chat
│   ├── utils/
│   │   ├── __init__.py
│   │   └── chunking.py      # Recursive text chunker with overlap
│   └── main.py              # FastAPI application and route handlers
├── static/
│   └── index.html           # Modern dark-themed chat interface
└── tests/
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures and Gemini mocks
    ├── test_api.py          # API endpoint tests via TestClient
    ├── test_chunking.py     # Chunking unit tests
    ├── test_schemas.py      # Schema validation tests
    └── test_vector_store.py # Vector distance calculation tests
```

---

## License

MIT License.
