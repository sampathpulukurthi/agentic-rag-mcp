"""API route definitions."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    QueryResult,
)
from app.core.rag import rag_pipeline
from app.core.fallback import firecrawl_search

from app.config import Settings, get_settings


api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.get("/health", summary="Health check")
def health_check(settings: Settings = Depends(get_settings)) -> dict:
    """Verify the API is running and return basic info."""

    return {
        "status": "ok",
        "service": "mcp-agentic-rag",
        "debug": settings.debug,
    }


@api_router.get("/config", summary="Get configuration")
def read_config(settings: Settings = Depends(get_settings)) -> dict:
    """Return non-sensitive configuration details."""

    return {
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "chroma_collection": settings.chroma_collection_name,
        "embedding_model": settings.embedding_model,
    }


@api_router.post("/ingest", response_model=IngestResponse, summary="Ingest documents")
def ingest_documents(payload: IngestRequest) -> IngestResponse:
    """Ingest documents into the RAG pipeline."""

    documents = [doc.text for doc in payload.documents]
    metadatas = [doc.metadata for doc in payload.documents]
    ids = [doc.id for doc in payload.documents]

    try:
        rag_pipeline.ingest(documents=documents, metadatas=metadatas, ids=ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IngestResponse(count=len(payload.documents), message="Documents ingested successfully")


@api_router.post("/query", response_model=QueryResponse, summary="Query the RAG pipeline")
def query_documents(payload: QueryRequest) -> QueryResponse:
    """Query similar documents from the vector store."""

    try:
        result = rag_pipeline.query(
            query_text=payload.query_text,
            k=payload.k,
            where=payload.where,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return QueryResponse(
        query=payload.query_text,
        results=QueryResult(
            ids=result.get("ids", [[]])[0],
            documents=result.get("documents", [[]])[0],
            metadatas=result.get("metadatas", [[]])[0],
            distances=result.get("distances", [[]])[0] if result.get("distances") else None,
        ),
    )



@api_router.post("/query_with_fallback", summary="Query the RAG pipeline with web fallback")
def query_with_fallback(payload: QueryRequest):
    """Query RAG and fall back to Firecrawl web search when no RAG matches found."""

    try:
        result = rag_pipeline.query(
            query_text=payload.query_text,
            k=payload.k,
            where=payload.where,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    documents = result.get("documents", [[]])[0]

    # If we have RAG documents, return the same shape as `/query` endpoint
    if documents:
        return QueryResponse(
            query=payload.query_text,
            results=QueryResult(
                ids=result.get("ids", [[]])[0],
                documents=documents,
                metadatas=result.get("metadatas", [[]])[0],
                distances=result.get("distances", [[]])[0] if result.get("distances") else None,
            ),
        )

    # No RAG matches — attempt Firecrawl fallback
    try:
        web_results = firecrawl_search(payload.query_text, limit=payload.k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"query": payload.query_text, "fallback": True, "web_results": web_results}

