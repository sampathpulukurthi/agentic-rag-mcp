"""Seed the Chroma database with FAQ entries."""

from __future__ import annotations

from app.core.rag import rag_pipeline
from app.data_seed import parse_faq


def seed_faq() -> None:
    """Ingest the FAQ dataset into Chroma."""

    entries = parse_faq()
    documents = [entry["text"] for entry in entries]
    metadatas = [
        {
            "id": entry["id"],
            "question": entry["question"],
            "answer": entry["answer"],
            "topic": "ml_faq",
        }
        for entry in entries
    ]
    ids = [entry["id"] for entry in entries]

    rag_pipeline.ingest(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Seeded {len(entries)} FAQ entries into Chroma")


if __name__ == "__main__":
    seed_faq()
