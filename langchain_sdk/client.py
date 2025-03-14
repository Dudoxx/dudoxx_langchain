"""
Client Library for Automated Large-Text Field Extraction Solution

This module provides a client library for interacting with the extraction pipeline
directly from Python code or with the API service.
"""

import os
import json
import asyncio
import requests
from typing import List, Dict, Any, Optional, Union, BinaryIO

# Import extraction pipeline components
from langchain_community.document_loaders import TextLoader, PyPDFLoader,  AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

from langchain_community.llms import OpenAI
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from langchain_community.embeddings import OpenAIEmbeddings

# Import custom components
try:
    # Try relative imports first (when used as a package)
    from .extraction_pipeline import ExtractionPipeline, TemporalNormalizer, ResultMerger, OutputFormatter
    from .configuration_service import ConfigurationService
    _local_imports_available = True
except ImportError:
    try:
        # Try absolute imports (when used directly)
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from langchain_sdk.extraction_pipeline import ExtractionPipeline, TemporalNormalizer, ResultMerger, OutputFormatter
        from langchain_sdk.configuration_service import ConfigurationService
        _local_imports_available = True
    except ImportError:
        _local_imports_available = False


# Define a dynamic Pydantic model for extraction
def create_extraction_model(fields: List[str], field_descriptions: Dict[str, str]) -> type:
    """
    Create a dynamic Pydantic model for extraction.
    
    Args:
        fields: List of field names
        field_descriptions: Dictionary of field descriptions
        
    Returns:
        Pydantic model class
    """
    field_annotations = {}
    field_defaults = {}
    
    for field in fields:
        # Set field type to Any
        field_annotations[field] = Optional[Any]
        
        # Set field description
        field_defaults[field] = Field(
            default=None,
            description=field_descriptions.get(field, f"Extract {field}")
        )
    
    # Create model
    model = type(
        "ExtractionModel",
        (BaseModel,),
        {
            "__annotations__": field_annotations,
            **field_defaults
        }
    )
    
    return model


class ExtractionClient:
    """
    Client for the Automated Large-Text Field Extraction Solution.
    
    This client can operate in two modes:
    1. Local mode: Uses the extraction pipeline directly
    2. API mode: Communicates with the API service
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config_dir: str = "./config",
        use_api: bool = False
    ):
        """
        Initialize the extraction client.
        
        Args:
            api_key: API key for authentication (required for API mode)
            base_url: Base URL of the API service (required for API mode)
            config_dir: Directory containing configuration files (for local mode)
            use_api: Whether to use the API service
        """
        self.api_key = api_key
        self.base_url = base_url
        self.config_dir = config_dir
        self.use_api = use_api
        
        # Initialize components for local mode
        if not use_api and _local_imports_available:
            self.config_service = ConfigurationService(config_dir)
            self.pipeline = None
        elif use_api and (not api_key or not base_url):
            raise ValueError("API key and base URL are required for API mode")
    
    async def _initialize_pipeline(self) -> None:
        """Initialize extraction pipeline for local mode."""
        if self.pipeline is not None:
            return
        
        # Get global configuration
        global_config = self.config_service.get_global_config()
        
        # Initialize components
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=global_config.get("chunking", {}).get("max_chunk_size", 16000),
            chunk_overlap=global_config.get("chunking", {}).get("overlap_size", 200),
            separators=["\n\n", "\n", " ", ""]
        )
        
        llm = OpenAI(
            model_name=global_config.get("extraction", {}).get("model_name", "gpt-4"),
            temperature=global_config.get("extraction", {}).get("temperature", 0.0),
            max_tokens=1000
        )
        
        # Initialize custom components
        temporal_normalizer = TemporalNormalizer(llm)
        result_merger = ResultMerger(
            embedding_model=OpenAIEmbeddings(),
            deduplication_threshold=global_config.get("merging", {}).get("deduplication_threshold", 0.9)
        )
        output_formatter = OutputFormatter()
        
        # Create extraction pipeline
        self.pipeline = ExtractionPipeline(
            document_loader=None,  # Will be set based on file type
            text_splitter=text_splitter,
            llm=llm,
            output_parser=None,  # Will be set based on fields
            temporal_normalizer=temporal_normalizer,
            result_merger=result_merger,
            output_formatter=output_formatter,
            max_concurrency=global_config.get("processing", {}).get("max_concurrency", 20)
        )
    
    async def extract_text(
        self,
        text: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"]
    ) -> Dict[str, Any]:
        """
        Extract structured information from text.
        
        Args:
            text: Text to extract from
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        if self.use_api:
            return await self._extract_text_api(text, fields, domain, output_formats)
        else:
            return await self._extract_text_local(text, fields, domain, output_formats)
    
    async def _extract_text_api(
        self,
        text: str,
        fields: List[str],
        domain: str,
        output_formats: List[str]
    ) -> Dict[str, Any]:
        """Extract text using API service."""
        url = f"{self.base_url}/api/v1/extract"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "document_text": text,
            "fields": fields,
            "domain": domain,
            "output_formats": output_formats
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    async def _extract_text_local(
        self,
        text: str,
        fields: List[str],
        domain: str,
        output_formats: List[str]
    ) -> Dict[str, Any]:
        """Extract text using local pipeline."""
        if not _local_imports_available:
            raise ImportError("Local imports not available. Install the required packages.")
        
        # Initialize pipeline if needed
        await self._initialize_pipeline()
        
        # Get domain configuration
        domain_config = self.config_service.get_domain_config(domain)
        if not domain_config:
            raise ValueError(f"Domain not found: {domain}")
        
        # Validate fields
        domain_fields = self.config_service.get_field_names(domain)
        for field in fields:
            if field not in domain_fields:
                raise ValueError(f"Invalid field for domain {domain}: {field}")
        
        # Get field descriptions
        field_descriptions = self.config_service.get_field_descriptions(fields)
        
        # Create dynamic Pydantic model
        extraction_model = create_extraction_model(fields, field_descriptions)
        
        # Create output parser
        output_parser = PydanticOutputParser(pydantic_object=extraction_model)
        
        # Set document loader and output parser
        self.pipeline.document_loader = TextLoader
        self.pipeline.output_parser = output_parser
        
        # Create temporary file for document text
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(text)
            temp_path = temp_file.name
        
        try:
            # Process document
            result = await self.pipeline.process_document(
                document_path=temp_path,
                fields=fields,
                domain=domain,
                output_formats=output_formats
            )
            
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def extract_file(
        self,
        file_path: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"]
    ) -> Dict[str, Any]:
        """
        Extract structured information from file.
        
        Args:
            file_path: Path to file
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        if self.use_api:
            return await self._extract_file_api(file_path, fields, domain, output_formats)
        else:
            return await self._extract_file_local(file_path, fields, domain, output_formats)
    
    async def _extract_file_api(
        self,
        file_path: str,
        fields: List[str],
        domain: str,
        output_formats: List[str]
    ) -> Dict[str, Any]:
        """Extract file using API service."""
        url = f"{self.base_url}/api/v1/extract/file"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "fields": fields,
            "domain": domain,
            "output_formats": output_formats
        }
        
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, params=params, files=files)
        
        response.raise_for_status()
        
        return response.json()
    
    async def _extract_file_local(
        self,
        file_path: str,
        fields: List[str],
        domain: str,
        output_formats: List[str]
    ) -> Dict[str, Any]:
        """Extract file using local pipeline."""
        if not _local_imports_available:
            raise ImportError("Local imports not available. Install the required packages.")
        
        # Initialize pipeline if needed
        await self._initialize_pipeline()
        
        # Get domain configuration
        domain_config = self.config_service.get_domain_config(domain)
        if not domain_config:
            raise ValueError(f"Domain not found: {domain}")
        
        # Validate fields
        domain_fields = self.config_service.get_field_names(domain)
        for field in fields:
            if field not in domain_fields:
                raise ValueError(f"Invalid field for domain {domain}: {field}")
        
        # Get field descriptions
        field_descriptions = self.config_service.get_field_descriptions(fields)
        
        # Create dynamic Pydantic model
        extraction_model = create_extraction_model(fields, field_descriptions)
        
        # Create output parser
        output_parser = PydanticOutputParser(pydantic_object=extraction_model)
        
        # Set output parser
        self.pipeline.output_parser = output_parser
        
        # Determine document loader based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".pdf":
            document_loader = PyPDFLoader
        elif file_extension == ".docx":
            document_loader = AzureAIDocumentIntelligenceLoader
        elif file_extension in [".txt", ".md", ".json", ".csv"]:
            document_loader = TextLoader
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Set document loader
        self.pipeline.document_loader = document_loader
        
        # Process document
        result = await self.pipeline.process_document(
            document_path=file_path,
            fields=fields,
            domain=domain,
            output_formats=output_formats
        )
        
        return result
    
    async def get_domains(self) -> List[Dict[str, Any]]:
        """
        Get available domains.
        
        Returns:
            List of domain information
        """
        if self.use_api:
            return await self._get_domains_api()
        else:
            return await self._get_domains_local()
    
    async def _get_domains_api(self) -> List[Dict[str, Any]]:
        """Get domains using API service."""
        url = f"{self.base_url}/api/v1/domains"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json().get("domains", [])
    
    async def _get_domains_local(self) -> List[Dict[str, Any]]:
        """Get domains using local configuration service."""
        if not _local_imports_available:
            raise ImportError("Local imports not available. Install the required packages.")
        
        return self.config_service.get_domains()
    
    async def get_domain_fields(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get fields for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of field information
        """
        if self.use_api:
            return await self._get_domain_fields_api(domain)
        else:
            return await self._get_domain_fields_local(domain)
    
    async def _get_domain_fields_api(self, domain: str) -> List[Dict[str, Any]]:
        """Get domain fields using API service."""
        url = f"{self.base_url}/api/v1/domains/{domain}/fields"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json().get("fields", [])
    
    async def _get_domain_fields_local(self, domain: str) -> List[Dict[str, Any]]:
        """Get domain fields using local configuration service."""
        if not _local_imports_available:
            raise ImportError("Local imports not available. Install the required packages.")
        
        domain_config = self.config_service.get_domain_config(domain)
        if not domain_config:
            raise ValueError(f"Domain not found: {domain}")
        
        return self.config_service.get_domain_fields(domain)


class ExtractionClientSync:
    """
    Synchronous client for the Automated Large-Text Field Extraction Solution.
    
    This client provides a synchronous interface to the extraction pipeline.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config_dir: str = "./config",
        use_api: bool = False
    ):
        """
        Initialize the synchronous extraction client.
        
        Args:
            api_key: API key for authentication (required for API mode)
            base_url: Base URL of the API service (required for API mode)
            config_dir: Directory containing configuration files (for local mode)
            use_api: Whether to use the API service
        """
        self.async_client = ExtractionClient(api_key, base_url, config_dir, use_api)
    
    def extract_text(
        self,
        text: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"]
    ) -> Dict[str, Any]:
        """
        Extract structured information from text.
        
        Args:
            text: Text to extract from
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        return asyncio.run(self.async_client.extract_text(text, fields, domain, output_formats))
    
    def extract_file(
        self,
        file_path: str,
        fields: List[str],
        domain: str,
        output_formats: List[str] = ["json", "text"]
    ) -> Dict[str, Any]:
        """
        Extract structured information from file.
        
        Args:
            file_path: Path to file
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        return asyncio.run(self.async_client.extract_file(file_path, fields, domain, output_formats))
    
    def get_domains(self) -> List[Dict[str, Any]]:
        """
        Get available domains.
        
        Returns:
            List of domain information
        """
        return asyncio.run(self.async_client.get_domains())
    
    def get_domain_fields(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get fields for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of field information
        """
        return asyncio.run(self.async_client.get_domain_fields(domain))


# Example usage
if __name__ == "__main__":
    # Synchronous client (local mode)
    client = ExtractionClientSync(config_dir="./config")
    
    # Get available domains
    domains = client.get_domains()
    print(f"Available domains: {domains}")
    
    # Get fields for medical domain
    fields = client.get_domain_fields("medical")
    print(f"Medical domain fields: {fields}")
    
    # Extract from text
    result = client.extract_text(
        text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
        fields=["patient_name", "date_of_birth", "diagnoses"],
        domain="medical"
    )
    
    # Print results
    print("\nExtraction result:")
    print(f"JSON output: {result.get('json_output')}")
    print(f"Text output: {result.get('text_output')}")
    print(f"Processing time: {result.get('metadata', {}).get('processing_time')} seconds")
