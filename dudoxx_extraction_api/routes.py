"""
Routes for the Dudoxx Extraction API.

This module defines the API routes for the extraction endpoints.
"""

import os
import tempfile
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Header, Form, Body, Query, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from rich.panel import Panel

from dudoxx_extraction_api.config import API_PREFIX, API_KEY
from dudoxx_extraction_api.progress_manager import add_progress_update, get_progress_endpoint, get_progress_callback
from dudoxx_extraction.progress_tracker import ProgressTracker, ExtractionPhase
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
    format_extraction_result,
    console
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


# Add SSE endpoint for progress updates
@router.get("/progress/{request_id}", tags=["Progress"])
async def progress_stream(
    request: Request, 
    request_id: str, 
    api_key: Optional[str] = Query(None, description="API key (can be provided in query parameter)")
):
    """
    Get progress updates for a specific request.
    
    This endpoint uses Server-Sent Events (SSE) to stream progress updates
    to the client in real-time.
    
    Args:
        request: FastAPI request object
        request_id: Unique identifier for the request
        api_key: API key (can be provided in query parameter)
        
    Returns:
        SSE stream of progress updates
    """
    # Verify API key from query parameter or header
    header_api_key = request.headers.get("X-API-Key")
    
    if not api_key and not header_api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key is required"
        )
    
    if (api_key and api_key != API_KEY) or (header_api_key and header_api_key != API_KEY):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    console.print(Panel(
        f"[bold blue]Client connected to progress stream for request {request_id}[/]",
        title="Progress Stream Request",
        border_style="blue"
    ))
    
    return get_progress_endpoint(request, request_id)


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
    request_id = str(uuid.uuid4())
    
    try:
        # Log request
        log_request(operation_type, request.dict())
        
        # Send initial progress update
        add_progress_update(request_id, "starting", "Starting extraction process...")
        
        # Identify domains and fields
        add_progress_update(request_id, "processing", "Identifying domains and fields...", 20)
        domain_identification, domain, fields = identify_domains_and_fields(request.text, request.query)
        
        # Use domain from request if provided
        if request.domain:
            domain = request.domain
        
        # Extract information
        add_progress_update(request_id, "processing", f"Extracting information using domain: {domain}...", 40)
        result = extract_from_text(
            text=request.text,
            query=request.query,
            domain=domain,
            output_formats=request.output_formats,
            use_parallel=use_parallel,
            request_id=request_id
        )
        
        # Send completion progress update
        add_progress_update(request_id, "completed", "Extraction completed successfully", 100)
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            domain_identification=domain_identification,
            extraction_result=format_extraction_result(result),
            query=request.query,
            domain=domain,
            fields=fields,
            request_id=request_id
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Send error progress update
        add_progress_update(request_id, "error", f"Extraction failed: {str(e)}", 100)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            query=request.query,
            domain=request.domain,
            request_id=request_id
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
    request_id = str(uuid.uuid4())
    
    try:
        # Log request
        log_request(operation_type, request.dict())
        
        # Send initial progress update
        add_progress_update(request_id, "starting", "Starting multi-query extraction process...")
        
        # Process each query
        all_results = {}
        all_domains = set()
        all_fields = set()
        primary_domain_identification = None
        
        total_queries = len(request.queries)
        for i, query in enumerate(request.queries):
            # Update progress
            progress_percentage = int(20 + (60 * (i / total_queries)))
            add_progress_update(
                request_id, 
                "processing", 
                f"Processing query {i+1}/{total_queries}: {query[:50]}...", 
                progress_percentage
            )
            
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
                use_parallel=use_parallel,
                request_id=request_id
            )
            
            # Store results
            all_results[query] = result
            all_domains.add(domain)
            all_fields.update(fields)
            
            # Store first domain identification for response
            if primary_domain_identification is None:
                primary_domain_identification = domain_identification
        
        # Merge results
        add_progress_update(request_id, "processing", "Merging results from all queries...", 90)
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
        
        # Send completion progress update
        add_progress_update(request_id, "completed", "Multi-query extraction completed successfully", 100)
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            domain_identification=primary_domain_identification,
            extraction_result=format_extraction_result(merged_result),
            queries=request.queries,
            domain=request.domain or ", ".join(all_domains),
            fields=list(all_fields),
            request_id=request_id
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Send error progress update
        add_progress_update(request_id, "error", f"Multi-query extraction failed: {str(e)}", 100)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            queries=request.queries,
            domain=request.domain,
            request_id=request_id
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
    request_id = str(uuid.uuid4())
    
    try:
        # Log request
        log_request(operation_type, {
            "file": file.filename,
            "query": query,
            "domain": domain,
            "output_formats": output_formats,
            "use_parallel": use_parallel
        })
        
        # Send initial progress update
        add_progress_update(request_id, "starting", f"Starting extraction from file: {file.filename}...")
        
        # Parse output formats
        output_formats_list = output_formats.split(",") if output_formats else None
        
        # Save file to temporary location
        add_progress_update(request_id, "processing", "Saving uploaded file...", 10)
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read file content for domain identification
        add_progress_update(request_id, "processing", "Analyzing file content...", 20)
        
        # First, try to identify domain from the query regardless of file type
        console.print(f"[bold blue]Identifying domain from query: {query}[/]")
        add_progress_update(request_id, "processing", "Identifying domain from query...", 25)
        
        # Use the domain identifier with just the query
        from dudoxx_extraction.domain_identifier import DomainIdentifier
        domain_identifier = DomainIdentifier()
        query_domain_identification = domain_identifier.identify_domains_for_query(query)
        
        # Get the primary domain from query analysis
        query_identified_domain = None
        
        # Convert the domain_identifier.py DomainIdentificationResult to models.py DomainIdentificationResult
        api_domain_identification = None
        if query_domain_identification:
            # Create a new DomainIdentificationResult using the API model
            from dudoxx_extraction_api.models import DomainIdentificationResult as ApiDomainIdentificationResult
            from dudoxx_extraction_api.models import DomainMatch as ApiDomainMatch
            from dudoxx_extraction_api.models import FieldMatch as ApiFieldMatch
            
            # Convert matched domains
            api_matched_domains = []
            for domain_match in query_domain_identification.matched_domains:
                api_matched_domains.append(ApiDomainMatch(
                    domain_name=domain_match.domain_name,
                    confidence=domain_match.confidence,
                    reason=domain_match.reason
                ))
            
            # Convert matched fields
            api_matched_fields = []
            for field_match in query_domain_identification.matched_fields:
                api_matched_fields.append(ApiFieldMatch(
                    domain_name=field_match.domain_name,
                    sub_domain_name=field_match.sub_domain_name,
                    field_name=field_match.field_name,
                    confidence=field_match.confidence,
                    reason=field_match.reason
                ))
            
            # Create API domain identification result
            api_domain_identification = ApiDomainIdentificationResult(
                matched_domains=api_matched_domains,
                matched_fields=api_matched_fields,
                recommended_domains=query_domain_identification.recommended_domains,
                recommended_fields=query_domain_identification.recommended_fields
            )
            
            # Get the primary domain
            if api_matched_domains:
                # Sort by confidence and get the highest confidence domain
                sorted_domains = sorted(
                    api_matched_domains, 
                    key=lambda x: x.confidence, 
                    reverse=True
                )
                if sorted_domains:
                    query_identified_domain = sorted_domains[0].domain_name
                    console.print(f"[green]Domain identified from query: {query_identified_domain}[/]")
        
        # Now try to read the file content
        try:
            with open(temp_file_path, "r") as f:
                text = f.read()
                
            # Identify domains and fields from text content
            add_progress_update(request_id, "processing", "Identifying domains and fields from content...", 30)
            domain_identification, identified_domain, fields = identify_domains_and_fields(text, query)
            
            console.print(f"[green]Domain identified from content: {identified_domain}[/]")
        except UnicodeDecodeError:
            # If file can't be read as text, use document loaders and the domain from query
            add_progress_update(request_id, "processing", "File is binary, using document loaders...", 30)
            
            # Use domain from query identification if available
            if query_identified_domain:
                identified_domain = query_identified_domain
                domain_identification = api_domain_identification
                console.print(f"[yellow]Binary file detected. Using domain from query: {identified_domain}[/]")
            else:
                # Use domain from request or default to "general"
                identified_domain = domain if domain else "general"
                domain_identification = None
                console.print(f"[yellow]Binary file detected. Using domain: {identified_domain}[/]")
            
            fields = []
        
        # Use domain from request if provided
        if domain:
            identified_domain = domain
        
        # Ensure we have a valid domain
        if not identified_domain:
            identified_domain = "general"
            console.print("[yellow]No domain identified or provided. Using default domain: general[/]")
            add_progress_update(request_id, "processing", "No domain identified. Using default domain: general", 35)
        
        # Extract information
        add_progress_update(
            request_id, 
            "processing", 
            f"Extracting information using domain: {identified_domain}...", 
            40
        )
        result = extract_from_file(
            file_path=temp_file_path,
            query=query,
            domain=identified_domain,
            output_formats=output_formats_list,
            use_parallel=use_parallel,
            request_id=request_id
        )
        
        # Send completion progress update
        add_progress_update(request_id, "completed", "File extraction completed successfully", 100)
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            domain_identification=domain_identification,
            extraction_result=format_extraction_result(result),
            query=query,
            domain=identified_domain,
            fields=fields,
            request_id=request_id
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Send error progress update
        add_progress_update(request_id, "error", f"File extraction failed: {str(e)}", 100)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            query=query,
            domain=domain,
            request_id=request_id
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
    request_id = str(uuid.uuid4())
    
    try:
        # Log request
        log_request(operation_type, {
            "file": file.filename,
            "domain": domain,
            "output_formats": output_formats
        })
        
        # Send initial progress update
        add_progress_update(
            request_id, 
            "starting", 
            f"Starting document extraction from {file.filename} using domain: {domain}..."
        )
        
        # Parse output formats
        output_formats_list = output_formats.split(",") if output_formats else None
        
        # Save file to temporary location
        add_progress_update(request_id, "processing", "Saving uploaded file...", 10)
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Use parallel extraction pipeline
        add_progress_update(
            request_id, 
            "processing", 
            "Processing document with parallel extraction pipeline...", 
            30
        )
        from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync
        
        result = extract_document_sync(
            document_path=temp_file_path,
            domain_name=domain,
            output_formats=output_formats_list,
            use_threads=True,
            request_id=request_id
        )
        
        # Send completion progress update
        add_progress_update(request_id, "completed", "Document extraction completed successfully", 100)
        
        # Create response
        response = ExtractionResponse(
            status=ExtractionStatus.SUCCESS,
            operation_type=operation_type,
            extraction_result=format_extraction_result(result),
            domain=domain,
            request_id=request_id
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    except Exception as e:
        # Log error
        log_error(operation_type, e)
        
        # Send error progress update
        add_progress_update(request_id, "error", f"Document extraction failed: {str(e)}", 100)
        
        # Create error response
        response = ExtractionResponse(
            status=ExtractionStatus.ERROR,
            operation_type=operation_type,
            error_message=str(e),
            domain=domain,
            request_id=request_id
        )
        
        # Log response
        log_response(operation_type, response.status, response.dict())
        
        return response
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
