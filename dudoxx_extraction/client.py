"""
Dudoxx Extraction - Client Library for Automated Large-Text Field Extraction Solution

This module provides a client library for interacting with the extraction pipeline
directly from Python code.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Union

# Try to import from langchain_openai (recommended)
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fall back to langchain_community if langchain_openai is not installed
    from langchain_community.chat_models import ChatOpenAI
    print("Warning: Using deprecated ChatOpenAI from langchain_community.")
    print("Consider installing langchain_openai: pip install langchain_openai")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Load .env file and override existing environment variables
    load_dotenv(override=True)
    
    # Get OpenAI settings from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
except ImportError:
    # python-dotenv not installed
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")

# Import extraction functions
try:
    # Try relative imports first (when used as a package)
    from .extraction_pipeline import extract_text as _extract_text, extract_file as _extract_file
except ImportError:
    # Try absolute imports (when used directly)
    try:
        from dudoxx_extraction.extraction_pipeline import extract_text as _extract_text, extract_file as _extract_file
    except ImportError:
        # Fall back to local imports
        from extraction_pipeline import extract_text as _extract_text, extract_file as _extract_file


class ExtractionClient:
    """
    Client for the Automated Large-Text Field Extraction Solution.
    
    This client provides an asynchronous interface to the extraction pipeline.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize the extraction client.
        
        Args:
            api_key: API key for OpenAI (defaults to OPENAI_API_KEY from .env)
            base_url: Base URL for OpenAI API (defaults to OPENAI_BASE_URL from .env)
            model_name: Model name to use (defaults to OPENAI_MODEL_NAME from .env)
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.base_url = base_url or OPENAI_BASE_URL
        self.model_name = model_name or OPENAI_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY in .env or pass api_key parameter.")
    
    async def extract_text(
        self,
        text: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"],
        use_query_preprocessor: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured information from text.
        
        Args:
            text: Text to extract from
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            use_query_preprocessor: Whether to use query preprocessing
            
        Returns:
            Extraction result
        """
        # Use the synchronous function in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _extract_text(text, fields, domain, output_formats, use_query_preprocessor)
        )
        
        return result
    
    async def extract_file(
        self,
        file_path: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"],
        use_query_preprocessor: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured information from file.
        
        Args:
            file_path: Path to file
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            use_query_preprocessor: Whether to use query preprocessing
            
        Returns:
            Extraction result
        """
        # Use the synchronous function in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _extract_file(file_path, fields, domain, output_formats, use_query_preprocessor)
        )
        
        return result


class ExtractionClientSync:
    """
    Synchronous client for the Automated Large-Text Field Extraction Solution.
    
    This client provides a synchronous interface to the extraction pipeline.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize the synchronous extraction client.
        
        Args:
            api_key: API key for OpenAI (defaults to OPENAI_API_KEY from .env)
            base_url: Base URL for OpenAI API (defaults to OPENAI_BASE_URL from .env)
            model_name: Model name to use (defaults to OPENAI_MODEL_NAME from .env)
        """
        self.async_client = ExtractionClient(api_key, base_url, model_name)
    
    def extract_text(
        self,
        text: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"],
        use_query_preprocessor: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured information from text.
        
        Args:
            text: Text to extract from
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            use_query_preprocessor: Whether to use query preprocessing
            
        Returns:
            Extraction result
        """
        return _extract_text(text, fields, domain, output_formats, use_query_preprocessor)
    
    def extract_file(
        self,
        file_path: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"],
        use_query_preprocessor: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured information from file.
        
        Args:
            file_path: Path to file
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            use_query_preprocessor: Whether to use query preprocessing
            
        Returns:
            Extraction result
        """
        return _extract_file(file_path, fields, domain, output_formats, use_query_preprocessor)


# Example usage
if __name__ == "__main__":
    # Synchronous client
    client = ExtractionClientSync()
    
    # Extract from text
    result = client.extract_text(
        text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
        fields=["patient_name", "date_of_birth", "diagnoses"],
        domain="medical"
    )
    
    # Print results
    print("\nExtraction result:")
    print(f"JSON output: {json.dumps(result.get('json_output', {}), indent=2)}")
    print(f"Text output: {result.get('text_output', '')}")
    print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0):.2f} seconds")
