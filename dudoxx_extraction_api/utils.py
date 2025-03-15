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


def identify_domains_and_fields(text: str, query: str) -> Tuple[DomainIdentificationResult, str, List[str]]:
    """
    Identify domains and fields for extraction based on text and query.
    
    Args:
        text: Text to extract from
        query: Query describing what to extract
        
    Returns:
        Tuple of (domain identification result, domain name, field names)
    """
    console.print("[bold]Identifying domains and fields...[/]")
    
    # Initialize domain identifier
    domain_identifier = DomainIdentifier()
    
    # Get extraction schema
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
    
    # Get domain matches
    for domain_name, subdomains in extraction_schema.items():
        matched_domains.append(DomainMatch(
            domain_name=domain_name,
            confidence=0.9,  # Placeholder confidence
            reason=f"Matched based on query: {query}"
        ))
        
        # Get field matches
        for subdomain_name, field_list in subdomains.items():
            for field_name, confidence in field_list:
                matched_fields.append(FieldMatch(
                    domain_name=domain_name,
                    sub_domain_name=subdomain_name,
                    field_name=field_name,
                    confidence=confidence,
                    reason=f"Matched based on query: {query}"
                ))
    
    # Create domain identification result
    domain_identification = DomainIdentificationResult(
        matched_domains=matched_domains,
        matched_fields=matched_fields,
        recommended_domains=[primary_domain],
        recommended_fields={primary_domain: fields}
    )
    
    return domain_identification, primary_domain, fields


def extract_from_text(text: str, query: str, domain: Optional[str] = None, output_formats: Optional[List[str]] = None, use_parallel: bool = False) -> Dict[str, Any]:
    """
    Extract information from text based on query.
    
    Args:
        text: Text to extract from
        query: Query describing what to extract
        domain: Optional domain to use for extraction
        output_formats: Output formats to generate
        use_parallel: Whether to use parallel extraction
        
    Returns:
        Extraction result
    """
    console.print("[bold]Extracting information from text...[/]")
    
    # Try to import socket manager for progress updates
    try:
        from dudoxx_extraction_api.socket_manager import emit_progress
        has_socket = True
    except (ImportError, Exception) as e:
        console.print(f"[yellow]Warning: Socket.IO not available: {e}[/]")
        has_socket = False
        
        # Define a dummy emit_progress function if the real one is not available
        def emit_progress(status, message, percentage=None):
            console.print(f"[blue]Progress update (no socket):[/] {status} - {message}")
    
    # Emit starting progress if socket is available
    if has_socket:
        emit_progress("starting", "Starting extraction process...")
    
    # Identify domains and fields if domain is not provided
    if not domain:
        domain_identification, domain, fields = identify_domains_and_fields(text, query)
        
        # If no domain was identified, use "general" as a fallback
        if not domain:
            console.print("[yellow]No domain identified for query, using 'general' domain as fallback[/]")
            if has_socket:
                emit_progress("processing", "No domain identified, using 'general' domain as fallback", 20)
            domain = "general"
            fields = ["content"]  # Generic field
    else:
        # Use domain identifier to get fields
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
            if has_socket:
                emit_progress("processing", f"No fields identified for domain {domain}, using generic approach", 30)
            fields = ["content"]  # Generic field
    
    # Set default output formats if not provided
    if not output_formats:
        output_formats = ["json", "text"]
    
    # Emit progress update for domain identification
    if has_socket:
        emit_progress("processing", f"Using domain: {domain}", 40)
    
    # Choose extraction method based on use_parallel flag
    if use_parallel:
        console.print("[bold]Using parallel extraction pipeline...[/]")
        if has_socket:
            emit_progress("processing", "Using parallel extraction pipeline...", 50)
        
        # Save text to temporary file for parallel extraction
        temp_file_path = save_temp_file(text)
        
        try:
            # Use parallel extraction pipeline
            result = extract_document_sync(
                document_path=temp_file_path,
                domain_name=domain,
                output_formats=output_formats
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    else:
        console.print("[bold]Using standard extraction pipeline...[/]")
        if has_socket:
            emit_progress("processing", "Using standard extraction pipeline...", 50)
        
        # Initialize extraction client
        client = ExtractionClientSync()
        
        # Extract information
        result = client.extract_text(
            text=text,
            fields=fields,
            domain=domain,
            output_formats=output_formats
        )
    
    console.print(f"[green]Extraction completed successfully[/]")
    
    # Emit completion progress if socket is available
    if has_socket:
        emit_progress("completed", "Extraction completed successfully", 100)
    
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


def extract_from_file(file_path: str, query: str, domain: Optional[str] = None, output_formats: Optional[List[str]] = None, use_parallel: bool = False) -> Dict[str, Any]:
    """
    Extract information from file based on query.
    
    Args:
        file_path: Path to file
        query: Query describing what to extract
        domain: Optional domain to use for extraction
        output_formats: Output formats to generate
        use_parallel: Whether to use parallel extraction
        
    Returns:
        Extraction result
    """
    console.print(f"[bold]Extracting information from file: {file_path}[/]")
    
    # Try to import socket manager for progress updates
    try:
        from dudoxx_extraction_api.socket_manager import emit_progress
        has_socket = True
    except (ImportError, Exception) as e:
        console.print(f"[yellow]Warning: Socket.IO not available: {e}[/]")
        has_socket = False
        
        # Define a dummy emit_progress function if the real one is not available
        def emit_progress(status, message, percentage=None):
            console.print(f"[blue]Progress update (no socket):[/] {status} - {message}")
    
    # Emit starting progress if socket is available
    if has_socket:
        emit_progress("starting", f"Starting extraction from file: {os.path.basename(file_path)}")
    
    # Check if file is supported by document loaders
    if DocumentLoaderFactory.is_supported_file(file_path):
        console.print(f"[green]File format supported by document loaders[/]")
        if has_socket:
            emit_progress("processing", "File format supported by document loaders", 20)
        
        if use_parallel:
            console.print("[bold]Using parallel extraction pipeline...[/]")
            if has_socket:
                emit_progress("processing", "Using parallel extraction pipeline...", 30)
            
            # Use parallel extraction pipeline with document loader
            result = extract_document_sync(
                document_path=file_path,
                domain_name=domain,
                output_formats=output_formats
            )
            
            # Emit completion progress if socket is available
            if has_socket:
                emit_progress("completed", "Extraction completed successfully", 100)
            
            return result
        else:
            # Load document using document loader factory
            if has_socket:
                emit_progress("processing", "Loading document...", 30)
            
            documents = DocumentLoaderFactory.load_document(file_path)
            
            # Combine document content
            if has_socket:
                emit_progress("processing", "Processing document content...", 40)
            
            text = "\n\n".join([doc.page_content for doc in documents])
            
            # Extract from text
            return extract_from_text(text, query, domain, output_formats)
    else:
        console.print(f"[yellow]File format not directly supported, falling back to basic text reading[/]")
        if has_socket:
            emit_progress("processing", "File format not directly supported, falling back to basic text reading", 20)
        
        # Read file content
        try:
            if has_socket:
                emit_progress("processing", "Reading file content...", 30)
            
            with open(file_path, 'r') as f:
                text = f.read()
        except UnicodeDecodeError:
            console.print(f"[red]Error reading file as text, file may be binary[/]")
            if has_socket:
                emit_progress("error", "Error reading file as text, file may be binary", 100)
            raise ValueError(f"File format not supported: {file_path}")
        
        # Extract from text
        return extract_from_text(text, query, domain, output_formats, use_parallel)


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
