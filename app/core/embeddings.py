"""Embedding utilities for the RAG pipeline."""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from sentence_transformers import SentenceTransformer

from app.config import Settings, get_settings


@lru_cache(maxsize=1)
def _get_model(model_name: str) -> SentenceTransformer:
    """Return a cached SentenceTransformer instance."""

    return SentenceTransformer(model_name)


def get_embedding_model(settings: Optional[Settings] = None) -> SentenceTransformer:
    """Get the embedding model configured in settings."""

    cfg = settings or get_settings()
    return _get_model(cfg.embedding_model)


def embed_texts(
    texts: List[str],
    model: Optional[SentenceTransformer] = None,
    settings: Optional[Settings] = None,
) -> List[List[float]]:
    """Generate embeddings for a list of texts."""

    embedding_model = model or get_embedding_model(settings)
    return embedding_model.encode(texts, convert_to_numpy=False).tolist()

