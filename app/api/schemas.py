"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentPayload(BaseModel):
    text: str = Field(..., description="Document text to ingest")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadata associated with the document"
    )
    id: Optional[str] = Field(default=None, description="Optional document ID")


class IngestRequest(BaseModel):
    documents: List[DocumentPayload] = Field(
        ..., min_length=1, description="List of documents to ingest"
    )


class IngestResponse(BaseModel):
    count: int
    message: str


class QueryRequest(BaseModel):
    query_text: str = Field(..., description="User query text")
    k: int = Field(default=5, ge=1, le=20, description="Number of results")
    where: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata filters"
    )


class QueryResult(BaseModel):
    ids: List[str]
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    distances: Optional[List[float]] = None


class QueryResponse(BaseModel):
    query: str
    results: QueryResult
