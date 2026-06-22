"""FastMCP server exposing RAG capabilities."""

from __future__ import annotations

from fastmcp.server import FastMCP

from app.core.rag import rag_pipeline
from app.core.fallback import firecrawl_search


server = FastMCP("mcp-agentic-rag")


@server.tool(description="Query the RAG knowledge base")
async def query_rag(query: str, k: int = 5) -> dict:
    """Return the top-k RAG matches for the given query."""

    result = rag_pipeline.query(query_text=query, k=k)
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    return {
        "query": query,
        "matches": [
            {
                "id": doc_id,
                "document": document,
                "metadata": metadata,
            }
            for doc_id, document, metadata in zip(ids, documents, metadatas)
        ],
    }



@server.tool(description="Query the RAG knowledge base with web fallback")
async def query_rag_with_fallback(query: str, k: int = 5) -> dict:
    """Return top-k RAG matches; fall back to Firecrawl web search when empty."""

    result = rag_pipeline.query(query_text=query, k=k)
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    if documents:
        return {
            "query": query,
            "matches": [
                {"id": doc_id, "document": document, "metadata": metadata}
                for doc_id, document, metadata in zip(ids, documents, metadatas)
            ],
            "fallback": False,
        }

    # No RAG matches -> attempt Firecrawl
    try:
        web = firecrawl_search(query, limit=k)
    except Exception as exc:
        return {"query": query, "matches": [], "fallback": True, "web_error": str(exc)}

    return {"query": query, "matches": [], "fallback": True, "web_results": web}


@server.tool(description="Seed the knowledge base with the ML FAQ dataset")
async def seed_faq() -> dict:
    """Seed Chroma with the default FAQ entries."""

    from app.data_seed import parse_faq

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

    return {"seeded": len(entries)}


if __name__ == "__main__":
    # When running under stdio transports (e.g., Windsurf MCP), any banner printed
    # to stdout corrupts the JSON-RPC handshake. Disable the FastMCP banner.
    server.run(show_banner=False)
