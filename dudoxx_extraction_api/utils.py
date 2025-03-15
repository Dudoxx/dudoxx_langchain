"""
Utility functions for the Dudoxx Extraction API.

This module provides utility functions for the API endpoints.
"""

import os
import tempfile
import traceback
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import Dudoxx Extraction components
from dudoxx_extraction.domain_identifier import DomainIdentifier
from dudoxx_extraction.extraction_pipeline import extract_text as dudoxx_extract_text
from dudoxx_extraction.client import ExtractionClientSync
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync
from dudoxx_extraction.document_loaders.document_loader_factory import DocumentLoaderFactory
from dudoxx_extraction.configuration_service import ConfigurationService

from dudoxx_extraction_api.models import (
    ExtractionStatus,
    OperationType,
    DomainIdentificationResult,
    ExtractionResult,
    DomainMatch,
    FieldMatch
)

# Initialize console for logging and configuration
console = Console()
config_service = ConfigurationService()


def log_request(operation_type: OperationType, request_data: Dict[str, Any]) -> None:
    """
    Log API request details.
    
    Args:
        operation_type: Type of extraction operation
        request_data: Request data
    """
    console.print(Panel(f"[bold blue]{operation_type.value.upper()}[/] Request", style="blue"))
    
    # Create table for request details
    table = Table(title="Request Details")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    # Add request parameters to table
    for key, value in request_data.items():
        if key == "text":
            # Truncate text to avoid cluttering the console
            text_preview = value[:100] + "..." if len(value) > 100 else value
            table.add_row(key, text_preview)
        else:
            table.add_row(key, str(value))
    
    console.print(table)


def log_response(operation_type: OperationType, status: ExtractionStatus, response_data: Dict[str, Any]) -> None:
    """
    Log API response details.
    
    Args:
        operation_type: Type of extraction operation
        status: Status of the extraction
        response_data: Response data
    """
    status_color = "green" if status == ExtractionStatus.SUCCESS else "red"
    console.print(Panel(f"[bold {status_color}]{operation_type.value.upper()}[/] Response: [bold {status_color}]{status.value.upper()}[/]", style=status_color))
    
    # Create table for response details
    table = Table(title="Response Details")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    # Add response parameters to table
    for key, value in response_data.items():
        if key in ["domain_identification", "extraction_result"]:
            # Skip complex objects
            continue
        elif key == "error_message" and value:
            table.add_row(key, f"[red]{value}[/]")
        else:
            table.add_row(key, str(value))
    
    console.print(table)
    
    # Log extraction result if available
    if "extraction_result" in response_data and response_data["extraction_result"]:
        console.print("[bold]Extraction Result:[/]")
        
        result = response_data["extraction_result"]
        if "json_output" in result and result["json_output"]:
            console.print("[cyan]JSON Output:[/]")
            console.print_json(data=result["json_output"])
        
        if "metadata" in result and result["metadata"]:
            console.print("[cyan]Metadata:[/]")
            for key, value in result["metadata"].items():
                console.print(f"  [green]{key}:[/] {value}")


def log_error(operation_type: OperationType, error: Exception) -> None:
    """
    Log API error details.
    
    Args:
        operation_type: Type of extraction operation
        error: Exception that occurred
    """
    console.print(Panel(f"[bold red]{operation_type.value.upper()}[/] Error", style="red"))
    console.print(f"[bold red]Error:[/] {str(error)}")
    console.print("[bold red]Traceback:[/]")
    console.print_exception()


def identify_domains_and_fields(text: str, query: str, use_query_preprocessor: bool = True) -> Tuple[DomainIdentificationResult, str, List[str]]:
    """
    Identify domains and fields for extraction based on text and query.
    
    Args:
        text: Text to extract from
        query: Query describing what to extract
        use_query_preprocessor: Whether to use query preprocessing
        
    Returns:
        Tuple of (domain identification result, domain name, field names)
    """
    console.print(f"[bold]Identifying domains and fields for query: '{query}'...[/]")
    
    # Preprocess the query if enabled
    if use_query_preprocessor:
        try:
            # Import query preprocessor
            from dudoxx_extraction.query_preprocessor import QueryPreprocessor
            
            # Initialize query preprocessor
            query_preprocessor = QueryPreprocessor(use_rich_logging=True)
            
            # Preprocess query
            console.print("[bold]Preprocessing query...[/]")
            preprocessed_query = query_preprocessor.preprocess_query(query)
            
            # Use preprocessed information if confidence is high enough
            if preprocessed_query.confidence >= 0.7:
                console.print(f"[green]Using preprocessed query: {preprocessed_query.reformulated_query}[/]")
                
                # If domain and fields are identified with high confidence, use them directly
                if preprocessed_query.identified_domain and preprocessed_query.identified_fields:
                    console.print(f"[green]Using identified domain: {preprocessed_query.identified_domain}[/]")
                    console.print(f"[green]Using identified fields: {', '.join(preprocessed_query.identified_fields)}[/]")
                    
                    # Create a domain identification result
                    domain_identification = DomainIdentificationResult(
                        matched_domains=[
                            DomainMatch(
                                domain_name=preprocessed_query.identified_domain,
                                confidence=preprocessed_query.confidence,
                                reason=f"Identified by query preprocessor with confidence {preprocessed_query.confidence:.2f}"
                            )
                        ],
                        matched_fields=[
                            FieldMatch(
                                domain_name=preprocessed_query.identified_domain,
                                sub_domain_name="default",  # This will be updated later
                                field_name=field,
                                confidence=preprocessed_query.confidence,
                                reason=f"Identified by query preprocessor with confidence {preprocessed_query.confidence:.2f}"
                            ) for field in preprocessed_query.identified_fields
                        ],
                        recommended_domains=[preprocessed_query.identified_domain],
                        recommended_fields={preprocessed_query.identified_domain: preprocessed_query.identified_fields}
                    )
                    
                    return domain_identification, preprocessed_query.identified_domain, preprocessed_query.identified_fields
                
                # If only domain is identified, use it with domain identifier for fields
                if preprocessed_query.identified_domain:
                    query = preprocessed_query.reformulated_query
                    domain = preprocessed_query.identified_domain
                    
                    # Initialize domain identifier with the identified domain
                    domain_identifier = DomainIdentifier(use_query_preprocessor=False)
                    
                    # Get extraction schema for the identified domain
                    extraction_schema = domain_identifier.get_extraction_schema(query)
                    
                    # If the identified domain is in the schema, use it
                    if preprocessed_query.identified_domain in extraction_schema:
                        console.print(f"[green]Using extraction schema for domain: {preprocessed_query.identified_domain}[/]")
                        return domain_identifier.identify_domains_for_query(query), preprocessed_query.identified_domain, preprocessed_query.identified_fields or []
                
                # Use the reformulated query with domain identifier
                query = preprocessed_query.reformulated_query
        except Exception as e:
            console.print(f"[red]Error using query preprocessor: {e}[/]")
            console.print("[yellow]Continuing with original query[/]")
    
    # Initialize domain identifier
    domain_identifier = DomainIdentifier(use_query_preprocessor=False)
    
    # Get extraction schema - this now uses the LLM to directly identify the most relevant domain and fields
    extraction_schema = domain_identifier.get_extraction_schema(query)
    
    # Get the primary domain (first domain in the schema)
    if not extraction_schema:
        console.print("[yellow]No domains identified for query, using 'general' domain as fallback[/]")
        
        # Create a fallback domain identification result
        domain_identification = DomainIdentificationResult(
            matched_domains=[
                DomainMatch(
                    domain_name="general",
                    confidence=0.6,
                    reason="Fallback domain for generic extraction"
                )
            ],
            matched_fields=[
                FieldMatch(
                    domain_name="general",
                    sub_domain_name="default",
                    field_name="content",
                    confidence=0.6,
                    reason="Generic content field for fallback extraction"
                )
            ],
            recommended_domains=["general"],
            recommended_fields={"general": ["content"]}
        )
        
        return domain_identification, "general", ["content"]
    
    primary_domain = next(iter(extraction_schema.keys()))
    console.print(f"[green]Primary domain identified:[/] {primary_domain}")
    
    # Get fields from all subdomains in the primary domain
    fields = []
    for subdomain, field_list in extraction_schema[primary_domain].items():
        for field_name, confidence in field_list:
            fields.append(field_name)
    
    # If no fields were identified, use a generic field
    if not fields:
        console.print(f"[yellow]No fields identified for domain {primary_domain}, using generic field[/]")
        fields = ["content"]
    else:
        console.print(f"[green]Fields identified:[/] {', '.join(fields)}")
    
    # Create domain identification result
    matched_domains = []
    matched_fields = []
    
    # Get domain matches - only include the primary domain for more focused extraction
    matched_domains.append(DomainMatch(
        domain_name=primary_domain,
        confidence=1.0,  # High confidence since we're using LLM for direct identification
        reason=f"Matched based on query: {query}"
    ))
    
    # Get field matches - only include fields from the primary domain
    for subdomain_name, field_list in extraction_schema[primary_domain].items():
        for field_name, confidence in field_list:
            matched_fields.append(FieldMatch(
                domain_name=primary_domain,
                sub_domain_name=subdomain_name,
                field_name=field_name,
                confidence=confidence,
                reason=f"Matched based on query: {query}"
            ))
    
    # Create domain identification result with focused recommendations
    domain_identification = DomainIdentificationResult(
        matched_domains=matched_domains,
        matched_fields=matched_fields,
        recommended_domains=[primary_domain],
        recommended_fields={primary_domain: fields}
    )
    
    return domain_identification, primary_domain, fields


# Get progress manager for emitting progress updates
try:
    from dudoxx_extraction_api.progress_manager import add_progress_update, get_progress_callback
    from dudoxx_extraction.progress_tracker import ProgressTracker, ExtractionPhase
    has_progress_manager = True
except (ImportError, Exception) as e:
    console.print(f"[yellow]Warning: Progress manager not available: {e}[/]")
    has_progress_manager = False
    
    # Define a dummy add_progress_update function if the real one is not available
    def add_progress_update(request_id, status, message, percentage=None):
        console.print(f"[blue]Progress update (no manager):[/] {status} - {message}")
    
    # Define a dummy get_progress_callback function
    def get_progress_callback():
        def progress_callback(request_id, status, message, percentage=None):
            console.print(f"[blue]Progress update (no manager):[/] {status} - {message} ({percentage}%)")
        return progress_callback


def emit_progress(request_id, status, message, percentage=None):
    """
    Emit progress update using the progress manager.
    
    Args:
        request_id: Request ID
        status: Status of the progress update
        message: Message for the progress update
        percentage: Percentage of completion (0-100)
    """
    if has_progress_manager:
        add_progress_update(request_id, status, message, percentage)
    else:
        console.print(f"[blue]Progress update:[/] {status} - {message} ({percentage}%)")


def extract_from_text(text: str, query: str, domain: Optional[str] = None, output_formats: Optional[List[str]] = None, use_parallel: bool = False, request_id: str = None, use_query_preprocessor: bool = True) -> Dict[str, Any]:
    """
    Extract information from text based on query.
    
    Args:
        text: Text to extract from
        query: Query describing what to extract
        domain: Optional domain to use for extraction
        output_formats: Output formats to generate
        use_parallel: Whether to use parallel extraction
        request_id: Request ID for progress updates
        use_query_preprocessor: Whether to use query preprocessing
        
    Returns:
        Extraction result
    """
    console.print("[bold]Extracting information from text...[/]")
    
    # Emit starting progress
    if request_id:
        emit_progress(request_id, "starting", "Starting extraction process...")
    
    # Identify domains and fields if domain is not provided
    if not domain:
        if request_id:
            emit_progress(request_id, "processing", "Identifying domains and fields...", 20)
        
        domain_identification, domain, fields = identify_domains_and_fields(text, query, use_query_preprocessor)
        
        # If no domain was identified, use "general" as a fallback
        if not domain:
            console.print("[yellow]No domain identified for query, using 'general' domain as fallback[/]")
            if request_id:
                emit_progress(request_id, "processing", "No domain identified, using 'general' domain as fallback", 20)
            domain = "general"
            fields = ["content"]  # Generic field
    else:
        # Use domain identifier to get fields
        if request_id:
            emit_progress(request_id, "processing", f"Identifying fields for domain: {domain}...", 20)
            
        domain_identifier = DomainIdentifier()
        extraction_schema = domain_identifier.get_extraction_schema(query)
        
        # Get fields from all subdomains in the specified domain
        fields = []
        if domain in extraction_schema:
            for subdomain, field_list in extraction_schema[domain].items():
                for field_name, confidence in field_list:
                    fields.append(field_name)
        
        # If no fields found, use a generic approach
        if not fields:
            console.print(f"[yellow]No fields identified for domain {domain}, using generic approach[/]")
            if request_id:
                emit_progress(request_id, "processing", f"No fields identified for domain {domain}, using generic approach", 30)
            fields = ["content"]  # Generic field
    
    # Set default output formats if not provided
    if not output_formats:
        output_formats = ["json", "text"]
    
    # Emit progress update for domain identification
    if request_id:
        emit_progress(request_id, "processing", f"Using domain: {domain} with fields: {', '.join(fields)}", 40)
    
    # Always use parallel extraction pipeline for consistency
    if use_parallel:
        console.print("[bold]Using parallel extraction pipeline...[/]")
        if request_id:
            emit_progress(request_id, "processing", "Using parallel extraction pipeline...", 50)
        
        # Save text to temporary file for parallel extraction
        temp_file_path = save_temp_file(text)
        
        try:
            # Use parallel extraction pipeline
            from dudoxx_extraction.domains.domain_registry import DomainRegistry
            
            # Get domain definition to get sub-domains
            domain_registry = DomainRegistry()
            domain_def = domain_registry.get_domain(domain)
            
            if domain_def:
                # Get sub-domains based on fields
                sub_domains = []
                field_to_subdomain = {}
                
                for sub_domain in domain_def.sub_domains:
                    sub_domain_fields = [field.name for field in sub_domain.fields]
                    matching_fields = [field for field in fields if field in sub_domain_fields]
                    
                    if matching_fields:
                        sub_domains.append(sub_domain.name)
                        for field in matching_fields:
                            field_to_subdomain[field] = sub_domain.name
                
                # Emit progress for each sub-domain
                if request_id and sub_domains:
                    for i, sub_domain in enumerate(sub_domains):
                        progress = 50 + (i * 40 // len(sub_domains))
                        emit_progress(
                            request_id, 
                            "processing", 
                            f"Processing sub-domain: {sub_domain}...", 
                            progress
                        )
                
                # Use parallel extraction pipeline with specific sub-domains
                result = extract_document_sync(
                    document_path=temp_file_path,
                    domain_name=domain,
                    sub_domain_names=sub_domains,
                    output_formats=output_formats,
                    request_id=request_id,
                    use_query_preprocessor=use_query_preprocessor
                )
            else:
                # Domain not found, use default extraction
                if request_id:
                    emit_progress(request_id, "processing", f"Domain '{domain}' not found, using default extraction...", 50)
                
                result = extract_document_sync(
                    document_path=temp_file_path,
                    domain_name=domain,
                    output_formats=output_formats,
                    request_id=request_id,
                    use_query_preprocessor=use_query_preprocessor
                )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    else:
        console.print("[bold]Using standard extraction pipeline...[/]")
        if request_id:
            emit_progress(request_id, "processing", "Using standard extraction pipeline...", 50)
        
        # Initialize extraction client
        client = ExtractionClientSync()
        
        # Emit progress for each field
        if request_id and fields:
            for i, field in enumerate(fields):
                progress = 50 + (i * 40 // len(fields))
                emit_progress(
                    request_id, 
                    "processing", 
                    f"Extracting field: {field}...", 
                    progress
                )
        
        # Extract information
        result = client.extract_text(
            text=text,
            fields=fields,
            domain=domain,
            output_formats=output_formats,
            use_query_preprocessor=use_query_preprocessor
        )
    
    console.print(f"[green]Extraction completed successfully[/]")
    
    # Emit completion progress
    if request_id:
        emit_progress(request_id, "completed", "Extraction completed successfully", 100)
    
    return result


def save_temp_file(content: str) -> str:
    """
    Save content to a temporary file.
    
    Args:
        content: Content to save
        
    Returns:
        Path to the temporary file
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=".txt")
    
    try:
        # Write content to file
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        
        return path
    except Exception as e:
        # Close file descriptor on error
        os.close(fd)
        raise e


def extract_from_file(file_path: str, query: str, domain: Optional[str] = None, output_formats: Optional[List[str]] = None, use_parallel: bool = False, request_id: str = None, use_query_preprocessor: bool = True) -> Dict[str, Any]:
    """
    Extract information from file based on query.
    
    Args:
        file_path: Path to file
        query: Query describing what to extract
        domain: Optional domain to use for extraction
        output_formats: Output formats to generate
        use_parallel: Whether to use parallel extraction
        request_id: Request ID for progress updates
        use_query_preprocessor: Whether to use query preprocessing
        
    Returns:
        Extraction result
    """
    console.print(f"[bold]Extracting information from file: {file_path}[/]")
    
    # Emit starting progress
    if request_id:
        emit_progress(request_id, "starting", f"Starting extraction from file: {os.path.basename(file_path)}")
    
    # Load document content
    try:
        # Check if file is supported by document loaders
        if DocumentLoaderFactory.is_supported_file(file_path):
            console.print(f"[green]File format supported by document loaders[/]")
            if request_id:
                emit_progress(request_id, "processing", "File format supported by document loaders", 20)
            
            # Load document using document loader factory
            if request_id:
                emit_progress(request_id, "processing", "Loading document...", 30)
            
            documents = DocumentLoaderFactory.load_document(file_path)
            
            # Combine document content
            if request_id:
                emit_progress(request_id, "processing", "Processing document content...", 40)
            
            text = "\n\n".join([doc.page_content for doc in documents])
        else:
            console.print(f"[yellow]File format not directly supported, falling back to basic text reading[/]")
            if request_id:
                emit_progress(request_id, "processing", "File format not directly supported, falling back to basic text reading", 20)
            
            # Read file content
            if request_id:
                emit_progress(request_id, "processing", "Reading file content...", 30)
            
            with open(file_path, 'r') as f:
                text = f.read()
    except UnicodeDecodeError:
        console.print(f"[red]Error reading file as text, file may be binary[/]")
        if request_id:
            emit_progress(request_id, "error", "Error reading file as text, file may be binary", 100)
        raise ValueError(f"File format not supported: {file_path}")
    
    # Now that we have the text, use the same extraction flow as extract_from_text
    return extract_from_text(text, query, domain, output_formats, use_parallel, request_id, use_query_preprocessor)


def format_extraction_result(result: Dict[str, Any]) -> ExtractionResult:
    """
    Format extraction result as ExtractionResult model.
    
    Args:
        result: Extraction result from client
        
    Returns:
        ExtractionResult model
    """
    return ExtractionResult(
        json_output=result.get("json_output"),
        text_output=result.get("text_output"),
        xml_output=result.get("xml_output"),
        metadata=result.get("metadata")
    )
