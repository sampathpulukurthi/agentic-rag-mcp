"""ChromaDB service utilities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import chromadb
from chromadb.api import Collection
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)

from app.config import Settings, get_settings


class ChromaService:
    """ChromaDB helper for managing collections and embeddings."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_dir
        )
        self.embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=self.settings.embedding_model
        )

    def get_collection(self, name: Optional[str] = None) -> Collection:
        """Get or create a Chroma collection with the configured embedding function."""

        collection_name = name or self.settings.chroma_collection_name

        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
        )

    def upsert_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Upsert documents into the Chroma collection."""

        collection = self.get_collection()

        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query the Chroma collection for similar documents."""

        collection = self.get_collection()

        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
        )


chroma_service = ChromaService()

