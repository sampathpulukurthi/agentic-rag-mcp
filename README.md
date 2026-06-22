# Agentic RAG MCP

A minimal FastAPI + FastMCP project that combines local RAG retrieval with Firecrawl web fallback.

## What this project does

- Loads a FastAPI application for document ingestion and vector queries.
- Uses ChromaDB for local vector storage and SentenceTransformers for embeddings.
- Provides an MCP tool server via `fastmcp` to expose RAG tools over stdio transport.
- Falls back to Firecrawl web search only when the local vector DB returns no documents.

## Repository structure

- `app/` - application source code
  - `api/` - FastAPI routes and schemas
  - `core/` - RAG logic, embeddings, fallback helper
  - `services/` - ChromaDB service integration
  - `mcp/` - FastMCP server entrypoint
- `scripts/` - utility scripts (seed data, etc.)
- `data/` - storage and persistence directories
- `.env.example` - environment variable template
- `pyproject.toml` - project dependencies and packaging config

## Setup for a new user

### 1. Clone the repository

```bash
git clone https://github.com/sampathpulukurthi/agentic-rag-mcp.git
cd agentic-rag-mcp
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -e .
```

### 4. Create environment variables

```bash
cp .env.example .env
```

Edit `.env` and set:

```ini
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 5. Run the FastAPI backend

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then verify:

```bash
curl http://127.0.0.1:8000/api/health
```

### 6. Run the MCP server

With the virtualenv active:

```bash
.venv/bin/python -m app.mcp.server
```

This starts the FastMCP server named `mcp-agentic-rag` using stdio transport.

## How to use

### Ingest documents

```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"id":"doc1","text":"Machine learning models can classify text.","metadata":{"topic":"ml"}}]}'
```

### Query local vector store

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query_text":"How do text classification models work?","k":3}'
```

### Query with fallback to Firecrawl

```bash
curl -X POST http://127.0.0.1:8000/api/query_with_fallback \
  -H "Content-Type: application/json" \
  -d '{"query_text":"What is machine learning?","k":5}'
```

If the vector store returns no documents, the endpoint will return `fallback: true` and `web_results` from Firecrawl.

## Notes

- There is currently no chat UI included in this repository.
- The app returns vector DB matches by default and only uses Firecrawl when local results are empty.
- If you want stronger fallback behavior, the `query_with_fallback` logic can be updated to use a similarity threshold.

