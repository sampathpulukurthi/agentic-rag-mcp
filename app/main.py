"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes import api_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    app = FastAPI(
        title="MCP Agentic RAG",
        description="API for managing MCP-powered Agentic RAG operations",
        version="0.1.0",
        debug=settings.debug,
    )

    app.include_router(api_router)

    return app


app = create_app()

