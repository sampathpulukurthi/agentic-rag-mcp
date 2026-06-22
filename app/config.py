"""Configuration management for MCP Agentic RAG application."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Firecrawl Configuration
    firecrawl_api_key: str = Field(..., description="Firecrawl API key")
    
    # Chroma Configuration
    chroma_persist_dir: str = Field(default="./data/chroma", description="Chroma persist directory")
    chroma_collection_name: str = Field(default="rag_documents", description="Chroma collection name")
    
    # Embedding Configuration
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Embedding model name")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings
