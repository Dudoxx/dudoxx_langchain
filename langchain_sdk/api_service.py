"""
API Service for Automated Large-Text Field Extraction Solution

This module provides a FastAPI web service for exposing the extraction pipeline.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Import client
try:
    from .client import ExtractionClient
except ImportError:
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from langchain_sdk.client import ExtractionClient
    except ImportError:
        raise ImportError("Client module not found")


# Create FastAPI app
app = FastAPI(
    title="Automated Large-Text Field Extraction API",
    description="API for extracting structured information from large text documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Models
class ExtractRequest(BaseModel):
    """Extract request model."""
    document_text: str = Field(..., description="Document text to extract from")
    fields: List[str] = Field(..., description="Fields to extract")
    domain: str = Field(..., description="Domain context")
    output_formats: List[str] = Field(default=["json", "text"], description="Output formats to generate")


class ExtractResponse(BaseModel):
    """Extract response model."""
    json_output: Optional[Dict[str, Any]] = Field(None, description="JSON output")
    text_output: Optional[str] = Field(None, description="Text output")
    xml_output: Optional[str] = Field(None, description="XML output")
    metadata: Dict[str, Any] = Field(..., description="Metadata")


class DomainInfo(BaseModel):
    """Domain information model."""
    name: str = Field(..., description="Domain name")
    description: str = Field(..., description="Domain description")
    fields: List[str] = Field(..., description="Available fields")


class DomainsResponse(BaseModel):
    """Domains response model."""
    domains: List[DomainInfo] = Field(..., description="Available domains")


class FieldInfo(BaseModel):
    """Field information model."""
    name: str = Field(..., description="Field name")
    description: str = Field(..., description="Field description")
    type: str = Field(..., description="Field type")
    is_unique: bool = Field(..., description="Whether the field is unique")


class FieldsResponse(BaseModel):
    """Fields response model."""
    fields: List[FieldInfo] = Field(..., description="Available fields")


# Authentication
async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Get API key from authorization header.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        API key
    """
    # In a real application, you would validate the API key against a database
    # For this example, we'll just return the token
    return credentials.credentials


# Routes
@app.post("/api/v1/extract", response_model=ExtractResponse)
async def extract(
    request: ExtractRequest,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Extract structured information from text.
    
    Args:
        request: Extract request
        api_key: API key
        
    Returns:
        Extraction result
    """
    try:
        # Initialize client
        client = ExtractionClient(api_key=api_key, use_api=False)
        
        # Extract information
        result = await client.extract_text(
            text=request.document_text,
            fields=request.fields,
            domain=request.domain,
            output_formats=request.output_formats
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/extract/file", response_model=ExtractResponse)
async def extract_file(
    file: UploadFile = File(...),
    fields: List[str] = Query(...),
    domain: str = Query(...),
    output_formats: List[str] = Query(["json", "text"]),
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Extract structured information from file.
    
    Args:
        file: File to extract from
        fields: Fields to extract
        domain: Domain context
        output_formats: Output formats to generate
        api_key: API key
        
    Returns:
        Extraction result
    """
    try:
        # Save file to temporary location
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Initialize client
        client = ExtractionClient(api_key=api_key, use_api=False)
        
        # Extract information
        result = await client.extract_file(
            file_path=file_path,
            fields=fields,
            domain=domain,
            output_formats=output_formats
        )
        
        # Clean up temporary file
        os.remove(file_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/domains", response_model=DomainsResponse)
async def get_domains(
    api_key: str = Depends(get_api_key)
) -> Dict[str, List[DomainInfo]]:
    """
    Get available domains.
    
    Args:
        api_key: API key
        
    Returns:
        Available domains
    """
    try:
        # Initialize client
        client = ExtractionClient(api_key=api_key, use_api=False)
        
        # Get domains
        domains = await client.get_domains()
        
        return {"domains": domains}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/domains/{domain}/fields", response_model=FieldsResponse)
async def get_domain_fields(
    domain: str,
    api_key: str = Depends(get_api_key)
) -> Dict[str, List[FieldInfo]]:
    """
    Get fields for a domain.
    
    Args:
        domain: Domain name
        api_key: API key
        
    Returns:
        Available fields
    """
    try:
        # Initialize client
        client = ExtractionClient(api_key=api_key, use_api=False)
        
        # Get fields
        fields = await client.get_domain_fields(domain)
        
        return {"fields": fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
