"""
Routes for the Dudoxx Extraction API.

This module defines the API routes for the extraction endpoints.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Header, Form, Body, Query
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from dudoxx_extraction_api.config import API_PREFIX, API_KEY
from dudoxx_extraction_api.models import (
    TextExtractionRequest,
    MultiQueryExtractionRequest,
    ExtractionResponse,
    ExtractionStatus,
    OperationType,
    HealthCheckResponse,
    ExtractionResult
)
from dudoxx_extraction_api.utils import (
    log_request,
    log_response,
    log_error,
    identify_domains_and_fields,
    extract_from_text,
    extract_from_file,
    save_temp_file,
    format_extraction_result
)

# Create API router
router = APIRouter(prefix=API_PREFIX)

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verify API key.
    
    Args:
        api_key: API key from header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health check response
    """
    return HealthCheckResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@router.post("/extract/text", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_text(
    request: TextExtractionRequest,
    use_parallel: bool = Query(False, description="Whether to use parallel extraction"),
    api_key: str = Depends(verify_api_key)
):
    """
    Extract information from text.
    
    Args:
        request: Text extraction request
        use_parallel: Whether to use parallel extraction
        api_key: API key
        
    Returns:
        Extraction response
    """
    operation_type = OperationType.TEXT_EXTRACTION
    
    try:
        # Log request
        log_request(operation_type, request.dict())
        
        # Identify domains and fields
        domain_identification, domain, fields = identify_domains_and_fields(request.text, request.query)
        
        # Use domain from request if provided
        if request.domain:
            domain = request.domain
        
        # Extract information
        result = extract_from_text(
            text=request.text,
            query=request.query,
            domain=domain,
            output_formats=request.output_formats,
            use_parallel=use_parallel
        )
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            domain_identification=domain_identification,
            extraction_result=format_extraction_result(result),
            query=request.query,
            domain=domain,
            fields=fields
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            query=request.query,
            domain=request.domain
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response


@router.post("/extract/multi-query", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_multi_query(
    request: MultiQueryExtractionRequest,
    use_parallel: bool = Query(False, description="Whether to use parallel extraction"),
    api_key: str = Depends(verify_api_key)
):
    """
    Extract information from text using multiple queries.
    
    Args:
        request: Multi-query extraction request
        use_parallel: Whether to use parallel extraction
        api_key: API key
        
    Returns:
        Extraction response
    """
    operation_type = OperationType.MULTI_QUERY_EXTRACTION
    
    try:
        # Log request
        log_request(operation_type, request.dict())
        
        # Process each query
        all_results = {}
        all_domains = set()
        all_fields = set()
        primary_domain_identification = None
        
        for query in request.queries:
            # Identify domains and fields
            domain_identification, domain, fields = identify_domains_and_fields(request.text, query)
            
            # Use domain from request if provided
            if request.domain:
                domain = request.domain
            
            # Extract information
            result = extract_from_text(
                text=request.text,
                query=query,
                domain=domain,
                output_formats=request.output_formats,
                use_parallel=use_parallel
            )
            
            # Store results
            all_results[query] = result
            all_domains.add(domain)
            all_fields.update(fields)
            
            # Store first domain identification for response
            if primary_domain_identification is None:
                primary_domain_identification = domain_identification
        
        # Merge results
        merged_result = {
            "json_output": {},
            "text_output": "",
            "metadata": {
                "query_count": len(request.queries),
                "processing_time": sum(r.get("metadata", {}).get("processing_time", 0) for r in all_results.values())
            }
        }
        
        # Merge JSON outputs
        for query, result in all_results.items():
            if "json_output" in result and result["json_output"]:
                merged_result["json_output"][query] = result["json_output"]
        
        # Merge text outputs
        for query, result in all_results.items():
            if "text_output" in result and result["text_output"]:
                merged_result["text_output"] += f"\n\n--- Results for query: {query} ---\n\n"
                merged_result["text_output"] += result["text_output"]
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            domain_identification=primary_domain_identification,
            extraction_result=format_extraction_result(merged_result),
            queries=request.queries,
            domain=request.domain or ", ".join(all_domains),
            fields=list(all_fields)
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            queries=request.queries,
            domain=request.domain
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response


@router.post("/extract/file", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_file(
    file: UploadFile = File(...),
    query: str = Form(...),
    domain: Optional[str] = Form(None),
    output_formats: Optional[str] = Form(None),
    use_parallel: bool = Form(False, description="Whether to use parallel extraction"),
    api_key: str = Depends(verify_api_key)
):
    """
    Extract information from file.
    
    Args:
        file: File to extract from
        query: Query describing what to extract
        domain: Optional domain to use for extraction
        output_formats: Output formats to generate (comma-separated)
        use_parallel: Whether to use parallel extraction
        api_key: API key
        
    Returns:
        Extraction response
    """
    operation_type = OperationType.FILE_EXTRACTION
    temp_file_path = None
    
    try:
        # Log request
        log_request(operation_type, {
            "file": file.filename,
            "query": query,
            "domain": domain,
            "output_formats": output_formats,
            "use_parallel": use_parallel
        })
        
        # Parse output formats
        output_formats_list = output_formats.split(",") if output_formats else None
        
        # Save file to temporary location
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read file content for domain identification
        try:
            with open(temp_file_path, "r") as f:
                text = f.read()
                
            # Identify domains and fields
            domain_identification, identified_domain, fields = identify_domains_and_fields(text, query)
        except UnicodeDecodeError:
            # If file can't be read as text, use document loaders
            domain_identification = None
            identified_domain = domain
            fields = []
        
        # Use domain from request if provided
        if domain:
            identified_domain = domain
        
        # Extract information
        result = extract_from_file(
            file_path=temp_file_path,
            query=query,
            domain=identified_domain,
            output_formats=output_formats_list,
            use_parallel=use_parallel
        )
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            domain_identification=domain_identification,
            extraction_result=format_extraction_result(result),
            query=query,
            domain=identified_domain,
            fields=fields
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            query=query,
            domain=domain
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.post("/extract/document", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_document(
    file: UploadFile = File(...),
    domain: str = Form(..., description="Domain to use for extraction"),
    output_formats: Optional[str] = Form(None),
    api_key: str = Depends(verify_api_key)
):
    """
    Extract information from document using parallel extraction pipeline.
    
    This endpoint uses the parallel extraction pipeline to extract all fields
    from a document based on the specified domain.
    
    Args:
        file: File to extract from
        domain: Domain to use for extraction
        output_formats: Output formats to generate (comma-separated)
        api_key: API key
        
    Returns:
        Extraction response
    """
    operation_type = OperationType.FILE_EXTRACTION
    temp_file_path = None
    
    try:
        # Log request
        log_request(operation_type, {
            "file": file.filename,
            "domain": domain,
            "output_formats": output_formats
        })
        
        # Parse output formats
        output_formats_list = output_formats.split(",") if output_formats else None
        
        # Save file to temporary location
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Use parallel extraction pipeline
        from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync
        
        result = extract_document_sync(
            document_path=temp_file_path,
            domain_name=domain,
            output_formats=output_formats_list
        )
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            extraction_result=format_extraction_result(result),
            domain=domain
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            domain=domain
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
