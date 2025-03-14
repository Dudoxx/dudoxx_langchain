# Environment Configuration

This document explains how to configure the Dudoxx Extraction system using environment variables, with a focus on the Dudoxx-specific configuration.

## Overview

The Dudoxx Extraction system uses environment variables for configuration, which can be loaded from `.env` files. This approach allows for flexible configuration without modifying the code.

## Configuration Files

The system supports two main configuration files:

1. **`.env`**: Standard environment configuration file
2. **`.env.dudoxx`**: Dudoxx-specific configuration file that overrides the standard configuration

## Dudoxx-Specific Configuration

The `.env.dudoxx` file contains Dudoxx-specific environment variables that override the standard OpenAI configuration:

```
DUDOXX_BASE_URL=https://llm-proxy.dudoxx.com/v1
DUDOXX_API_KEY=your-api-key
DUDOXX_MODEL_NAME=dudoxx
DUDOXX_EMBEDDING_MODEL=embedder
```

These variables are used to configure the Dudoxx LLM and embedding models, which are used for document extraction.

## Configuration Variables

A comprehensive list of all configuration variables is available in the `sample-env.env` file in the project root. Here's an overview of the main categories:

### Standard OpenAI Variables

The standard OpenAI variables are used as fallbacks if the Dudoxx-specific variables are not set:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_BASE_URL` | Base URL for the OpenAI API | `https://api.openai.com/v1` |
| `OPENAI_API_KEY` | API key for the OpenAI API | None (required) |
| `OPENAI_MODEL_NAME` | Name of the OpenAI model to use | `gpt-4` |
| `OPENAI_EMBEDDING_MODEL` | Name of the OpenAI embedding model to use | `text-embedding-ada-002` |

### Dudoxx-Specific Variables

The Dudoxx-specific variables override the standard OpenAI variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DUDOXX_BASE_URL` | Base URL for the Dudoxx API | `https://llm-proxy.dudoxx.com/v1` |
| `DUDOXX_API_KEY` | API key for the Dudoxx API | None (required) |
| `DUDOXX_MODEL_NAME` | Name of the Dudoxx model to use | `dudoxx` |
| `DUDOXX_EMBEDDING_MODEL` | Name of the Dudoxx embedding model to use | `embedder` |

### LLM Parameters

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_TEMPERATURE` | Temperature parameter for the LLM | `0` |
| `LLM_MAX_TOKENS` | Maximum number of tokens to generate | `4000` |
| `LLM_TOP_P` | Top-p sampling parameter | `1.0` |
| `LLM_FREQUENCY_PENALTY` | Frequency penalty parameter | `0.0` |
| `LLM_PRESENCE_PENALTY` | Presence penalty parameter | `0.0` |
| `LLM_TIMEOUT` | Timeout for LLM requests in seconds | `60` |

### Extraction Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `EXTRACTION_CHUNK_SIZE` | Size of document chunks in characters | `16000` |
| `EXTRACTION_CHUNK_OVERLAP` | Overlap between document chunks in characters | `200` |
| `EXTRACTION_MAX_CONCURRENCY` | Maximum number of concurrent LLM requests | `20` |
| `EXTRACTION_DEDUPLICATION_THRESHOLD` | Threshold for deduplication (0.0-1.0) | `0.9` |
| `EXTRACTION_DEFAULT_OUTPUT_FORMATS` | Default output formats (comma-separated) | `json,text` |
| `EXTRACTION_INCLUDE_METADATA` | Whether to include metadata in output | `true` |
| `EXTRACTION_DEFAULT_DOMAIN` | Default domain for extraction | `general` |
| `EXTRACTION_TEMPLATES_DIR` | Directory for domain-specific templates | `templates` |

### Logging Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `LOG_RICH_ENABLED` | Whether to enable rich logging | `true` |
| `LOG_VERBOSE` | Whether to enable verbose logging | `false` |
| `LOG_FILE` | File to write logs to | `extraction.log` |

### Cache and Vector Store Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CACHE_ENABLED` | Whether to enable caching | `true` |
| `CACHE_DIR` | Directory for cache files | `.cache` |
| `CACHE_TTL` | Time-to-live for cache entries in seconds | `86400` |
| `VECTOR_STORE_TYPE` | Type of vector store to use | `faiss` |
| `VECTOR_STORE_PATH` | Path to vector store files | `.vectorstore` |

## Loading Environment Variables

The system uses the `python-dotenv` library to load environment variables from `.env` files. The variables are loaded in the following order:

1. System environment variables
2. Variables from `.env` file
3. Variables from `.env.dudoxx` file (overriding previous values)

## Usage in Code

The environment variables are used in the code to configure the LLM and embedding models:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env and .env.dudoxx
load_dotenv()
load_dotenv(".env.dudoxx", override=True)

# Get configuration from environment variables
base_url = os.getenv("DUDOXX_BASE_URL", os.getenv("OPENAI_BASE_URL"))
api_key = os.getenv("DUDOXX_API_KEY", os.getenv("OPENAI_API_KEY"))
model_name = os.getenv("DUDOXX_MODEL_NAME", os.getenv("OPENAI_MODEL_NAME"))
embedding_model = os.getenv("DUDOXX_EMBEDDING_MODEL", os.getenv("OPENAI_EMBEDDING_MODEL"))

# Create LLM and embedding models
llm = ChatOpenAI(
    base_url=base_url,
    api_key=api_key,
    model_name=model_name
)

embeddings = OpenAIEmbeddings(
    base_url=base_url,
    api_key=api_key,
    model=embedding_model
)
```

## Configuration Service

The system includes a `ConfigurationService` class that handles loading and accessing environment variables:

```python
from dotenv import load_dotenv
import os

class ConfigurationService:
    def __init__(self):
        # Load environment variables from .env and .env.dudoxx
        load_dotenv()
        load_dotenv(".env.dudoxx", override=True)
        
    def get_llm_config(self):
        return {
            "base_url": os.getenv("DUDOXX_BASE_URL", os.getenv("OPENAI_BASE_URL")),
            "api_key": os.getenv("DUDOXX_API_KEY", os.getenv("OPENAI_API_KEY")),
            "model_name": os.getenv("DUDOXX_MODEL_NAME", os.getenv("OPENAI_MODEL_NAME"))
        }
        
    def get_embedding_config(self):
        return {
            "base_url": os.getenv("DUDOXX_BASE_URL", os.getenv("OPENAI_BASE_URL")),
            "api_key": os.getenv("DUDOXX_API_KEY", os.getenv("OPENAI_API_KEY")),
            "model": os.getenv("DUDOXX_EMBEDDING_MODEL", os.getenv("OPENAI_EMBEDDING_MODEL"))
        }
```

## Setting Up Configuration

To set up the configuration:

1. Create a `.env` file in the project root with standard configuration:

```
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_NAME=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

2. Create a `.env.dudoxx` file in the project root with Dudoxx-specific configuration:

```
DUDOXX_BASE_URL=https://llm-proxy.dudoxx.com/v1
DUDOXX_API_KEY=your-dudoxx-api-key
DUDOXX_MODEL_NAME=dudoxx
DUDOXX_EMBEDDING_MODEL=embedder
```

3. Make sure both files are included in `.gitignore` to avoid committing sensitive information.

## Best Practices

1. **Never commit API keys**: Always keep API keys out of version control.
2. **Use environment variables**: Avoid hardcoding configuration values in the code.
3. **Provide defaults**: Always provide sensible defaults for optional configuration values.
4. **Document configuration**: Document all configuration variables and their purpose.
5. **Validate configuration**: Validate configuration values at startup to catch errors early.
