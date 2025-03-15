"""
Configuration module for the Dudoxx Extraction API.

This module loads configuration from the .env.dudoxx file and provides
access to the configuration values.
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from rich.console import Console

# Initialize console for logging
console = Console()

# Load environment variables from .env.dudoxx file
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.dudoxx')
if os.path.exists(env_file):
    load_dotenv(env_file)
    console.print(f"[green]Loaded configuration from {env_file}[/]")
else:
    console.print(f"[yellow]Warning: Configuration file {env_file} not found. Using default values.[/]")

# API Configuration
API_TITLE = "Dudoxx Extraction API"
API_DESCRIPTION = "API for extracting structured information from text documents using LLM technology"
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Security Configuration
API_KEY = os.getenv("DUDOXX_API_KEY")
if not API_KEY:
    console.print("[bold red]Error: DUDOXX_API_KEY not found in environment variables[/]")
    raise ValueError("DUDOXX_API_KEY is required")

# LLM Configuration
LLM_CONFIG = {
    "base_url": os.getenv("DUDOXX_BASE_URL", "https://llm-proxy.dudoxx.com/v1"),
    "api_key": API_KEY,
    "model_name": os.getenv("DUDOXX_MODEL_NAME", "dudoxx"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4000")),
    "top_p": float(os.getenv("LLM_TOP_P", "1.0")),
    "frequency_penalty": float(os.getenv("LLM_FREQUENCY_PENALTY", "0.0")),
    "presence_penalty": float(os.getenv("LLM_PRESENCE_PENALTY", "0.0")),
    "timeout": int(os.getenv("LLM_TIMEOUT", "60"))
}

# Embedding Configuration
EMBEDDING_CONFIG = {
    "model": os.getenv("DUDOXX_EMBEDDING_MODEL", "embedder"),
    "api_key": API_KEY,
    "base_url": os.getenv("DUDOXX_BASE_URL", "https://llm-proxy.dudoxx.com/v1")
}

# Extraction Configuration
EXTRACTION_CONFIG = {
    "chunk_size": int(os.getenv("EXTRACTION_CHUNK_SIZE", "16000")),
    "chunk_overlap": int(os.getenv("EXTRACTION_CHUNK_OVERLAP", "200")),
    "max_concurrency": int(os.getenv("EXTRACTION_MAX_CONCURRENCY", "20")),
    "deduplication_threshold": float(os.getenv("EXTRACTION_DEDUPLICATION_THRESHOLD", "0.9")),
    "default_output_formats": os.getenv("EXTRACTION_DEFAULT_OUTPUT_FORMATS", "json,text").split(","),
    "include_metadata": os.getenv("EXTRACTION_INCLUDE_METADATA", "true").lower() == "true",
    "default_domain": os.getenv("EXTRACTION_DEFAULT_DOMAIN", "general")
}

# Logging Configuration
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "rich_enabled": os.getenv("LOG_RICH_ENABLED", "true").lower() == "true",
    "verbose": os.getenv("LOG_VERBOSE", "true").lower() == "true",
    "file": os.getenv("LOG_FILE", "dudoxx_extraction.log")
}

# Cache Configuration
CACHE_CONFIG = {
    "enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
    "dir": os.getenv("CACHE_DIR", ".dudoxx_cache"),
    "ttl": int(os.getenv("CACHE_TTL", "86400"))
}

# Vector Store Configuration
VECTOR_STORE_CONFIG = {
    "type": os.getenv("VECTOR_STORE_TYPE", "faiss"),
    "path": os.getenv("VECTOR_STORE_PATH", ".dudoxx_vectorstore")
}

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration."""
    return LLM_CONFIG

def get_embedding_config() -> Dict[str, Any]:
    """Get embedding configuration."""
    return EMBEDDING_CONFIG

def get_extraction_config() -> Dict[str, Any]:
    """Get extraction configuration."""
    return EXTRACTION_CONFIG

def get_log_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return LOG_CONFIG

def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    return CACHE_CONFIG

def get_vector_store_config() -> Dict[str, Any]:
    """Get vector store configuration."""
    return VECTOR_STORE_CONFIG
