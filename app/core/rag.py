"""Core RAG pipeline utilities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.embeddings import embed_texts, get_embedding_model
from app.services.chroma import ChromaService, chroma_service


class RagPipeline:
    """Simple wrapper around embeddings + Chroma operations."""

    def __init__(self, chroma: Optional[ChromaService] = None) -> None:
        self.chroma = chroma or chroma_service

    def ingest(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Embed and store documents in the vector database."""

        if not documents:
            raise ValueError("No documents provided for ingestion")

        if ids and len(ids) != len(documents):
            raise ValueError("Number of ids must match number of documents")

        if metadatas and len(metadatas) != len(documents):
            raise ValueError("Number of metadatas must match number of documents")

        # Embeddings handled automatically by Chroma's embedding function
        self.chroma.upsert_documents(documents=documents, metadatas=metadatas, ids=ids)

    def query(
        self,
        query_text: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query similar documents from the vector database."""

        if not query_text:
            raise ValueError("Query text cannot be empty")

        return self.chroma.query(query_texts=[query_text], n_results=k, where=where)


rag_pipeline = RagPipeline()

