# Testing Guide

This guide will help you test the RAG Engine API once you have PostgreSQL and Gemini API configured.

## Prerequisites Checklist

- [ ] PostgreSQL installed and running
- [ ] pgvector extension installed in PostgreSQL
- [ ] Database created (e.g., `ragdb`)
- [ ] `.env` file configured with:
  - `DATABASE_URL` (e.g., `postgresql://user:password@localhost:5432/ragdb`)
  - `GEMINI_API_KEY` (your Google Gemini API key)
- [ ] All Python dependencies installed (`pip install -r requirements.txt`)

## Step 1: Verify Setup

Run the verification script to check your setup:

```bash
python scripts/verify_setup.py
```

This will check:
- Package installations
- Code structure
- Environment file existence
- Environment variables

## Step 2: Initialize Database

Initialize the database and add sample data:

```bash
python scripts/init_db.py
```

This will:
- Create the `document_chunks` table
- Enable pgvector extension
- Add 5 sample document chunks for testing

## Step 3: Start the API Server

Start the FastAPI server:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## Step 4: Test the API

### Option A: Use the Test Scripts

**Windows:**
```bash
test_api.bat
```

**Linux/Mac:**
```bash
bash test_api.sh
```

### Option B: Manual Testing with curl

#### 1. Health Check
```bash
curl -X GET http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "rag-engine"
}
```

#### 2. Basic Query (Cosine Similarity)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python programming language?",
    "search_type": "cosine",
    "top_k": 3
  }'
```

#### 3. Query with L2 Distance
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does FastAPI work?",
    "search_type": "l2",
    "top_k": 2
  }'
```

#### 4. Query with Inner Product
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about vector embeddings",
    "search_type": "inner_product",
    "top_k": 5
  }'
```

#### 5. Query with Threshold Filter
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database systems",
    "search_type": "cosine",
    "top_k": 10,
    "threshold": 0.5
  }'
```

### Option C: Use Interactive API Documentation

FastAPI provides automatic interactive documentation:

1. Open your browser and navigate to:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

2. Use the interactive interface to test endpoints

## Expected Response Format

A successful query response will look like:

```json
{
  "query": "What is Python?",
  "chunks": [
    {
      "id": 1,
      "content": "Python is a high-level programming language...",
      "metadata": "{\"topic\": \"programming\", \"language\": \"python\"}",
      "document_id": "doc1",
      "chunk_index": 0,
      "similarity": 0.8523
    }
  ],
  "search_type": "cosine",
  "top_k": 1
}
```

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env` is correct
- Ensure database exists
- Verify pgvector extension is installed: `CREATE EXTENSION IF NOT EXISTS vector;`

### Gemini API Error
- Verify `GEMINI_API_KEY` is set correctly in `.env`
- Check your API key is valid and has access to text-embedding-001 model
- Ensure you have internet connectivity

### No Results Returned
- Make sure you ran `python scripts/init_db.py` to add sample data
- Check that chunks exist in the database: `SELECT COUNT(*) FROM document_chunks;`
- Verify embeddings were generated successfully

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.8+: `python --version`
- Verify you're in the project root directory

## Adding Your Own Data

To add your own document chunks, you can:

1. Use SQL directly:
```sql
INSERT INTO document_chunks (content, embedding, metadata, document_id, chunk_index)
VALUES (
  'Your text content here',
  '[your embedding vector array]',
  '{"key": "value"}',
  'your_doc_id',
  0
);
```

2. Or modify `scripts/init_db.py` to add your own chunks programmatically.

## Performance Tips

- Create an index on the embedding column for faster searches:
  ```sql
  CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
  ```
- Adjust `top_k` parameter based on your needs (lower = faster)
- Use threshold filtering to reduce unnecessary results

