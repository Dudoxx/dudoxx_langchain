"""
Configuration service for the Dudoxx Extraction system.

This module provides a configuration service that loads environment variables
from .env and .env.dudoxx files and provides access to configuration values.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional


class ConfigurationService:
    """
    Configuration service for the Dudoxx Extraction system.

    This class loads environment variables from .env and .env.dudoxx files
    and provides access to configuration values.

    Attributes:
        _config: Dictionary containing all configuration values.
    """

    def __init__(self):
        """
        Initialize the configuration service.

        Loads environment variables from .env and .env.dudoxx files.
        """
        # Load environment variables from .env and .env.dudoxx
        load_dotenv()
        load_dotenv(".env.dudoxx", override=True)
        
        # Initialize config dictionary
        self._config = {}
        
        # Load configuration values
        self._load_config()
        
    def _load_config(self):
        """
        Load configuration values from environment variables.
        """
        # LLM configuration
        self._config["llm"] = {
            "base_url": os.getenv("DUDOXX_BASE_URL", os.getenv("OPENAI_BASE_URL")),
            "api_key": os.getenv("DUDOXX_API_KEY", os.getenv("OPENAI_API_KEY")),
            "model_name": os.getenv("DUDOXX_MODEL_NAME", os.getenv("OPENAI_MODEL_NAME")),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4000")),
        }
        
        # Embedding configuration
        self._config["embedding"] = {
            "base_url": os.getenv("DUDOXX_BASE_URL", os.getenv("OPENAI_BASE_URL")),
            "api_key": os.getenv("DUDOXX_API_KEY", os.getenv("OPENAI_API_KEY")),
            "model": os.getenv("DUDOXX_EMBEDDING_MODEL", os.getenv("OPENAI_EMBEDDING_MODEL")),
        }
        
        # Extraction configuration
        self._config["extraction"] = {
            "chunk_size": int(os.getenv("EXTRACTION_CHUNK_SIZE", "16000")),
            "chunk_overlap": int(os.getenv("EXTRACTION_CHUNK_OVERLAP", "200")),
            "max_concurrency": int(os.getenv("EXTRACTION_MAX_CONCURRENCY", "20")),
        }
        
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get the LLM configuration.

        Returns:
            Dict[str, Any]: Dictionary containing LLM configuration values.
        """
        return self._config["llm"]
        
    def get_embedding_config(self) -> Dict[str, Any]:
        """
        Get the embedding configuration.

        Returns:
            Dict[str, Any]: Dictionary containing embedding configuration values.
        """
        return self._config["embedding"]
        
    def get_extraction_config(self) -> Dict[str, Any]:
        """
        Get the extraction configuration.

        Returns:
            Dict[str, Any]: Dictionary containing extraction configuration values.
        """
        return self._config["extraction"]
        
    def get_config_value(self, section: str, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a specific configuration value.

        Args:
            section: Configuration section.
            key: Configuration key.
            default: Default value if the key is not found.

        Returns:
            Any: Configuration value.
        """
        if section not in self._config:
            return default
            
        return self._config[section].get(key, default)
        
    def validate_config(self) -> bool:
        """
        Validate the configuration.

        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        # Check if required configuration values are present
        if not self._config["llm"]["base_url"]:
            return False
            
        if not self._config["llm"]["api_key"]:
            return False
            
        if not self._config["llm"]["model_name"]:
            return False
            
        if not self._config["embedding"]["model"]:
            return False
            
        return True
