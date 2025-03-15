"""
Pydantic models for the Dudoxx Extraction API.

This module defines the request and response models for the API endpoints.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class OperationType(str, Enum):
    """Type of extraction operation."""
    TEXT_EXTRACTION = "text_extraction"
    FILE_EXTRACTION = "file_extraction"
    QUERY_EXTRACTION = "query_extraction"
    MULTI_QUERY_EXTRACTION = "multi_query_extraction"


class ExtractionStatus(str, Enum):
    """Status of extraction operation."""
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"


class TextExtractionRequest(BaseModel):
    """Request model for text extraction."""
    text: str = Field(..., description="Text to extract information from")
    query: str = Field(..., description="Query describing what to extract")
    domain: Optional[str] = Field(None, description="Optional domain to use for extraction")
    output_formats: Optional[List[str]] = Field(None, description="Output formats to generate")

    class Config:
        schema_extra = {
            "example": {
                "text": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
                "query": "Extract patient information and diagnosis",
                "domain": "medical",
                "output_formats": ["json", "text"]
            }
        }


class MultiQueryExtractionRequest(BaseModel):
    """Request model for multi-query text extraction."""
    text: str = Field(..., description="Text to extract information from")
    queries: List[str] = Field(..., description="List of queries describing what to extract")
    domain: Optional[str] = Field(None, description="Optional domain to use for extraction")
    output_formats: Optional[List[str]] = Field(None, description="Output formats to generate")

    class Config:
        schema_extra = {
            "example": {
                "text": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
                "queries": [
                    "Extract patient information",
                    "Extract diagnosis information"
                ],
                "domain": "medical",
                "output_formats": ["json", "text"]
            }
        }

    @validator('queries')
    def validate_queries(cls, v):
        """Validate that queries list is not empty."""
        if not v:
            raise ValueError("queries list cannot be empty")
        return v


class DomainMatch(BaseModel):
    """Model for a matched domain."""
    domain_name: str = Field(..., description="Name of the matched domain")
    confidence: float = Field(..., description="Confidence score for the match (0-1)")
    reason: str = Field(..., description="Reason for the match")


class FieldMatch(BaseModel):
    """Model for a matched field."""
    domain_name: str = Field(..., description="Name of the parent domain")
    sub_domain_name: str = Field(..., description="Name of the parent sub-domain")
    field_name: str = Field(..., description="Name of the matched field")
    confidence: float = Field(..., description="Confidence score for the match (0-1)")
    reason: str = Field(..., description="Reason for the match")


class ExtractionResult(BaseModel):
    """Model for extraction result."""
    json_output: Optional[Dict[str, Any]] = Field(None, description="Extracted data in JSON format")
    text_output: Optional[str] = Field(None, description="Extracted data in text format")
    xml_output: Optional[str] = Field(None, description="Extracted data in XML format")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata about the extraction")


class DomainIdentificationResult(BaseModel):
    """Model for domain identification result."""
    matched_domains: List[DomainMatch] = Field(..., description="List of matched domains")
    matched_fields: List[FieldMatch] = Field(..., description="List of matched fields")
    recommended_domains: List[str] = Field(..., description="List of recommended domain names")
    recommended_fields: Dict[str, List[str]] = Field(..., description="Dictionary mapping domain names to lists of recommended field names")


class ExtractionResponse(BaseModel):
    """Response model for extraction endpoints."""
    status: ExtractionStatus = Field(..., description="Status of the extraction")
    operation_type: OperationType = Field(..., description="Type of extraction operation")
    error_message: Optional[str] = Field(None, description="Error message if status is ERROR")
    domain_identification: Optional[DomainIdentificationResult] = Field(None, description="Domain identification result")
    extraction_result: Optional[ExtractionResult] = Field(None, description="Extraction result")
    query: Optional[str] = Field(None, description="Query used for extraction")
    queries: Optional[List[str]] = Field(None, description="Queries used for multi-query extraction")
    domain: Optional[str] = Field(None, description="Domain used for extraction")
    fields: Optional[List[str]] = Field(None, description="Fields extracted")


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Status of the API")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
