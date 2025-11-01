# RAG Engine API

A production-ready **Retrieval Augmented Generation (RAG)** API built with FastAPI, FAISS vector database, and Google Gemini AI. This system combines semantic search with conversational AI to provide context-aware responses from your knowledge base.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [How RAG Works](#how-rag-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Interactive UI](#interactive-ui)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## 🎯 Overview

The RAG Engine API is a complete solution for building AI-powered applications with semantic search and conversational capabilities. It provides:

- **Semantic Search**: Find relevant content using vector similarity search
- **Conversational AI**: Chat with context-aware AI that understands your knowledge base
- **Easy Integration**: RESTful API that works with any frontend or application
- **Zero Infrastructure**: Uses FAISS for local vector storage (no external databases required)

### What is RAG?

Retrieval Augmented Generation (RAG) combines:
1. **Retrieval**: Semantic search to find relevant information from your knowledge base
2. **Augmentation**: Context from retrieved documents enhances the AI's knowledge
3. **Generation**: AI generates accurate, context-aware responses

This results in AI responses that are grounded in your specific data, reducing hallucinations and improving accuracy.

## ✨ Features

### Core Features
- **FastAPI REST API** - Modern, async Python web framework
- **FAISS Vector Database** - Pure Python, no external dependencies
- **Google Gemini Integration**:
  - `text-embedding-004` for generating embeddings (768 dimensions)
  - `gemini-2.0-flash` for conversational AI responses
- **Semantic Search** - Three search types: cosine similarity, L2 distance, inner product
- **Conversational Chat** - Multi-turn conversations with history maintenance
- **Interactive UI** - OpenAI-style chat interface for testing

### Advanced Features
- **Conversation History** - Maintains context across multiple chat turns
- **Configurable Parameters** - Adjust search types, top-K, temperature, and thresholds
- **Metadata Support** - Tag and filter content with custom metadata
- **Automatic Embeddings** - Content automatically embedded on addition
- **Local Storage** - All data stored locally in `faiss_db/` directory

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   FastAPI App   │  ← REST API Server
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼─────────────┐
│ FAISS │ │ Gemini API      │
│  DB   │ │ - Embeddings    │
│       │ │ - Chat (Flash)  │
└───────┘ └─────────────────┘
```

### Data Flow

#### Adding Content Flow:
```
User Input → Generate Embedding → Store in FAISS → Ready for Search
```

#### Chat/Query Flow:
```
User Query → Generate Query Embedding → Search FAISS → 
Retrieve Top-K Chunks → Combine with History → 
Send to Gemini LLM → Return Response
```

### Technology Stack

- **Backend**: FastAPI (Python)
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Google Gemini `text-embedding-004`
- **LLM**: Google Gemini `gemini-2.0-flash-exp`
- **Storage**: Local filesystem (`faiss_db/` directory)

## 🔄 How RAG Works

### Step-by-Step Process

#### 1. Content Ingestion
When you add content via `POST /content`:
- Content is sent to Gemini API to generate embeddings
- Embedding is a 768-dimensional vector representing semantic meaning
- Vector and metadata are stored in FAISS index
- Content is immediately searchable

#### 2. Query Processing
When you query via `POST /query` or `POST /chat`:
1. **Embedding Generation**: Query is converted to embedding vector
2. **Similarity Search**: FAISS finds most similar vectors using:
   - **Cosine Similarity**: Measures angle between vectors (0-1, higher = more similar)
   - **L2 Distance**: Euclidean distance (lower = more similar)
   - **Inner Product**: Dot product (higher = more similar)
3. **Ranking**: Results sorted by similarity score
4. **Retrieval**: Top-K most similar chunks returned

#### 3. Chat Enhancement (POST /chat)
For conversational responses:
1. **RAG Retrieval**: Relevant chunks retrieved as above
2. **History Integration**: Previous conversation messages included
3. **Context Building**: System prompt + RAG context + conversation history + current message
4. **LLM Generation**: Gemini Flash generates context-aware response
5. **Response Return**: AI response with metadata about context used

### Vector Embeddings Explained

Embeddings convert text into numerical vectors that capture semantic meaning:
- Similar texts have similar embeddings (close in vector space)
- Enables semantic search beyond keyword matching
- Example: "Python programming" and "coding in Python" would have similar embeddings

## 📦 Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **pip** (Python package manager)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-engine
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `faiss-cpu` - Vector database
- `google-generativeai` - Gemini API client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Initialize the Database

```bash
python scripts/init_db.py
```

This will:
- Create the FAISS index
- Add sample data for testing
- Verify the setup

### 5. Start the Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive UI**: `http://localhost:8000/`
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ Yes |
| `API_HOST` | Server host | `0.0.0.0` | No |
| `API_PORT` | Server port | `8000` | No |

### FAISS Storage

- **Location**: `faiss_db/` directory
- **Files**:
  - `index.faiss` - Vector index
  - `metadata.pkl` - Content metadata
- **Persistence**: Data persists across restarts
- **Backup**: Simply copy the `faiss_db/` directory

## 📡 API Endpoints

### `GET /health`

Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-engine"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### `POST /content`

Add new document content to the vector database. Content is automatically embedded and becomes searchable immediately.

**Request Body:**
```json
{
  "content": "Your document content here. This will be embedded and stored.",
  "document_id": "doc1",           // Optional: Document identifier
  "chunk_index": 0,                 // Optional: Chunk position in document
  "metadata": {                     // Optional: Custom metadata
    "topic": "AI",
    "source": "book",
    "author": "John Doe"
  }
}
```

**Response:**
```json
{
  "chunk_id": 5,
  "content": "Your document content here...",
  "document_id": "doc1",
  "chunk_index": 0,
  "message": "Content added successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Machine learning is a subset of AI that enables systems to learn from data.",
    "document_id": "ml_intro",
    "metadata": {"topic": "machine learning", "level": "beginner"}
  }'
```

**Use Cases:**
- Adding documentation
- Indexing articles or blog posts
- Building a knowledge base
- Storing FAQ content

---

### `POST /query`

Semantic search endpoint. Returns relevant document chunks based on similarity search.

**Request Body:**
```json
{
  "query": "What is Python?",
  "search_type": "cosine",          // Optional: "cosine", "l2", or "inner_product"
  "top_k": 5,                       // Optional: Number of results (1-100)
  "threshold": 0.5,                 // Optional: Minimum similarity (0.0-1.0)
  "metadata_filter": null           // Optional: Filter by metadata (not implemented)
}
```

**Response:**
```json
{
  "query": "What is Python?",
  "chunks": [
    {
      "id": 0,
      "content": "Python is a high-level programming language...",
      "metadata": "{\"topic\": \"programming\", \"language\": \"python\"}",
      "document_id": "doc1",
      "chunk_index": 0,
      "similarity": 0.7688
    }
  ],
  "search_type": "cosine",
  "top_k": 1
}
```

**Search Types:**
- **`cosine`**: Cosine similarity (0-1, higher = more similar) - Recommended for most cases
- **`l2`**: Euclidean distance (lower = more similar) - Good for comparing magnitudes
- **`inner_product`**: Dot product (higher = more similar) - Fast but less intuitive

**Reranking:**
Reranking improves search accuracy by:
1. Retrieving `top_k * 2` initial candidates
2. Re-embedding the query and all candidates for fresh similarity scores
3. Re-sorting by new similarity scores
4. Returning the top `rerank_top_k` (or `top_k`) most relevant results

**When to use reranking:**
- When precision is more important than speed
- For complex queries where semantic meaning matters
- When initial search results don't match well
- Note: Reranking adds latency (requires additional API calls)

**Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "search_type": "cosine",
    "top_k": 3,
    "threshold": 0.6
  }'
```

---

### `POST /chat`

Conversational chat endpoint with RAG. Returns AI-generated responses using your knowledge base and conversation history.

**Request Body:**
```json
{
  "message": "What is machine learning?",
  "conversation_history": [         // Optional: Previous messages
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "search_type": "cosine",         // Optional: "cosine", "l2", or "inner_product"
  "top_k": 3,                       // Optional: Context chunks to retrieve (1-10)
  "temperature": 0.7,               // Optional: LLM creativity (0.0-1.0)
  "system_prompt": null            // Optional: Custom system prompt
}
```

**Response:**
```json
{
  "response": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. Based on the context from your knowledge base...",
  "user_message": "What is machine learning?",
  "context_used": 3,
  "context_chunks": [
    {
      "content": "Machine learning is a subset of AI...",
      "similarity": 0.8523
    }
  ],
  "model": "gemini-2.0-flash-exp"
}
```

**Parameters:**
- **`temperature`**: Controls randomness (0.0 = deterministic, 1.0 = creative)
- **`top_k`**: Number of RAG context chunks (fewer = more focused, more = broader context)
- **`conversation_history`**: Previous messages for context-aware responses

**Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain deep learning",
    "top_k": 3,
    "temperature": 0.8
  }'
```

**Conversation Example:**
```bash
# First message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'

# Response includes conversation_history for next call
# Second message (with history)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are its main uses?",
    "conversation_history": [
      {"role": "user", "content": "What is Python?"},
      {"role": "assistant", "content": "Python is a high-level..."}
    ]
  }'
```

---

## 💡 Usage Examples

### Complete Workflow Example

```python
import requests

API_URL = "http://localhost:8000"

# 1. Add content to knowledge base
content_response = requests.post(f"{API_URL}/content", json={
    "content": "FastAPI is a modern web framework for building APIs with Python.",
    "document_id": "fastapi_doc",
    "metadata": {"topic": "web development", "framework": "FastAPI"}
})
print(f"Added content: {content_response.json()['chunk_id']}")

# 2. Search for relevant content
query_response = requests.post(f"{API_URL}/query", json={
    "query": "web frameworks",
    "search_type": "cosine",
    "top_k": 3
})
chunks = query_response.json()['chunks']
print(f"Found {len(chunks)} relevant chunks")

# 3. Chat with RAG context
chat_response = requests.post(f"{API_URL}/chat", json={
    "message": "What is FastAPI?",
    "top_k": 3,
    "temperature": 0.7
})
print(f"AI Response: {chat_response.json()['response']}")

# 4. Continue conversation
conversation_history = [
    {"role": "user", "content": "What is FastAPI?"},
    {"role": "assistant", "content": chat_response.json()['response']}
]

followup_response = requests.post(f"{API_URL}/chat", json={
    "message": "How do I use it?",
    "conversation_history": conversation_history,
    "top_k": 3
})
print(f"Follow-up Response: {followup_response.json()['response']}")
```

### JavaScript Example

```javascript
const API_URL = 'http://localhost:8000';

// Add content
async function addContent(content, metadata = {}) {
  const response = await fetch(`${API_URL}/content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content,
      metadata
    })
  });
  return await response.json();
}

// Query
async function query(query, topK = 5) {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      search_type: 'cosine',
      top_k: topK
    })
  });
  return await response.json();
}

// Chat
let conversationHistory = [];

async function chat(message) {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
      top_k: 3,
      temperature: 0.7
    })
  });
  
  const data = await response.json();
  
  // Update conversation history
  conversationHistory.push({ role: 'user', content: message });
  conversationHistory.push({ role: 'assistant', content: data.response });
  
  // Keep last 10 exchanges
  if (conversationHistory.length > 20) {
    conversationHistory = conversationHistory.slice(-20);
  }
  
  return data;
}

// Usage
await addContent('Python is a versatile programming language.');
const results = await query('programming languages');
const chatResponse = await chat('Tell me about Python');
```

## 🖥️ Interactive UI

Access the OpenAI-style chat interface at `http://localhost:8000/`

### Features:
- **Chat Interface**: Natural conversation with RAG-powered AI
- **Query Testing**: Search your knowledge base
- **Content Management**: Add new content easily
- **Parameter Configuration**: Adjust search types, top-K, thresholds
- **Real-time Responses**: See JSON responses formatted nicely

### UI Endpoints:
- **Chat Mode**: Select `/chat` from sidebar for conversational AI
- **Query Mode**: Select `/query` for semantic search
- **Content Mode**: Select `/content` to add new documents

## 📁 Project Structure

```
rag-engine/
├── src/
│   ├── __init__.py              # Package marker
│   ├── main.py                  # FastAPI application and endpoints
│   ├── config.py                # Configuration and environment variables
│   ├── services_faiss.py        # RAG service with FAISS integration
│   ├── faiss_db.py              # FAISS database operations
│   ├── models.py                # Data models (legacy, for PostgreSQL)
│   └── database.py              # Database utilities (legacy)
│
├── scripts/
│   ├── init_db.py               # Initialize FAISS database with sample data
│   ├── test_api.py              # Comprehensive API test suite
│   ├── test_content_endpoint.py # Test content addition
│   ├── verify_setup.py          # Verify installation and setup
│   └── ...                      # Other utility scripts
│
├── static/
│   └── index.html               # OpenAI-style interactive UI
│
├── faiss_db/                    # FAISS vector database storage
│   ├── index.faiss              # Vector index file
│   └── metadata.pkl             # Content metadata
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Environment variable template
├── README.md                    # This file
└── test_*.py                    # Test scripts
```

### Key Files Explained

- **`src/main.py`**: Main FastAPI application with all endpoints
- **`src/services_faiss.py`**: Core RAG logic, embedding generation, and chat functionality
- **`src/faiss_db.py`**: FAISS database operations (add, search, manage)
- **`scripts/init_db.py`**: Database initialization with sample data
- **`static/index.html`**: Interactive web UI for testing

## 📦 Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.104.1 | Modern web framework |
| `uvicorn` | 0.24.0 | ASGI server |
| `faiss-cpu` | 1.7.4 | Vector similarity search |
| `google-generativeai` | 0.3.2 | Gemini API client |
| `pydantic` | 2.5.0 | Data validation |
| `python-dotenv` | 1.0.0 | Environment variables |
| `numpy` | 1.26.2 | Numerical operations |
| `requests` | 2.32.5 | HTTP client (for tests) |

### Installation

```bash
pip install -r requirements.txt
```

## 🧪 Testing

### Automated Tests

Run the comprehensive test suite:

```bash
python scripts/test_api.py
```

This tests:
- Health check endpoint
- Content addition
- Query endpoint (all search types)
- Chat endpoint
- Threshold filtering

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Add content
curl -X POST http://localhost:8000/content \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 3}'

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "top_k": 3}'
```

### Test Scripts

- **`test_api.py`**: Comprehensive API test suite
- **`test_chat_endpoint.py`**: Test chat functionality
- **`test_conversational_chat.py`**: Test conversation history
- **`test_add_and_fetch.py`**: Test content addition and retrieval

## 🔧 Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "GEMINI_API_KEY not found"
- Verify `.env` file exists
- Check that `GEMINI_API_KEY` is set correctly
- Ensure `.env` is in the project root

#### 3. "FAISS index not found"
```bash
# Reinitialize database
python scripts/init_db.py
```

#### 4. API returns 500 errors
- Check Gemini API key is valid
- Verify API key has proper permissions
- Check server logs for detailed error messages

#### 5. Slow responses
- Reduce `top_k` parameter
- Check network connection to Gemini API
- Consider reducing conversation history length

### Debugging

Enable debug mode:
```bash
uvicorn src.main:app --reload --log-level debug
```

Check logs:
- Server output shows detailed error messages
- Gemini API errors are returned in response body

### Getting Help

1. Check the Swagger docs: `http://localhost:8000/docs`
2. Review test scripts for usage examples
3. Check server logs for error details

## 🛠️ Development

### Running in Development Mode

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Adding New Features

1. **New Endpoint**: Add to `src/main.py`
2. **Service Logic**: Add to `src/services_faiss.py`
3. **UI Updates**: Modify `static/index.html`

### Code Structure

- **Endpoints**: Defined in `src/main.py` with Pydantic models
- **Business Logic**: Implemented in `src/services_faiss.py`
- **Database**: FAISS operations in `src/faiss_db.py`
- **Configuration**: Environment variables in `src/config.py`

### Best Practices

1. **Error Handling**: All endpoints use try-except blocks
2. **Validation**: Pydantic models validate all inputs
3. **Type Hints**: All functions use type annotations
4. **Documentation**: Docstrings explain all functions

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set `GEMINI_API_KEY` securely
2. **Server**: Use production ASGI server (not `--reload`)
3. **Backup**: Regularly backup `faiss_db/` directory
4. **Monitoring**: Add logging and monitoring
5. **Rate Limiting**: Consider adding rate limits

### Example Production Command

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future)

The project includes `docker-compose.yml` for PostgreSQL (legacy). FAISS doesn't require Docker, but you can containerize the FastAPI app if needed.

## 📊 Performance

- **Embedding Generation**: ~200-500ms per content
- **Search**: <10ms for typical queries
- **Chat Response**: ~1-3s (includes RAG + LLM)
- **Storage**: ~1KB per chunk (embedding + metadata)

### Optimization Tips

- Reduce `top_k` for faster searches
- Limit conversation history (last 10-20 messages)
- Batch content additions when possible
- Use cosine similarity for best performance

## 🔐 Security

### Current Security

- Input validation via Pydantic
- Error messages don't expose sensitive data
- Environment variables for API keys

### Recommended Enhancements

- Add API authentication (JWT tokens)
- Rate limiting per IP/user
- Input sanitization for content
- HTTPS in production
- API key rotation

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional search algorithms
- Advanced metadata filtering
- Batch operations
- Performance optimizations
- UI enhancements

## 📚 Additional Resources

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [RAG Research Papers](https://arxiv.org/abs/2005.11401)

---

**Built with ❤️ using FastAPI, FAISS, and Google Gemini**
