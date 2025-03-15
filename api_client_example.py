"""
API Client Example for Dudoxx Extraction API.

This script demonstrates how to use the Dudoxx Extraction API by sending
data and queries from the ./data/ folder to the API.

The script showcases five different extraction scenarios:
1. Text extraction with a single query
2. Text extraction with multiple queries
3. File extraction
4. Document extraction using parallel processing
5. Text extraction with parallel processing

Usage:
    python api_client_example.py

Requirements:
    - Running Dudoxx Extraction API server (python dudoxx_extraction_api/main.py)
    - .env.dudoxx file with API key
    - requests, rich, and python-dotenv packages
"""

import os
import re
import json
import requests
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from dotenv import load_dotenv

# Load environment variables from .env.dudoxx file
load_dotenv('.env.dudoxx')

# Initialize console for logging
console = Console()

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("DUDOXX_API_KEY")

if not API_KEY:
    console.print("[bold red]Error: DUDOXX_API_KEY not found in environment variables[/]")
    exit(1)

# Headers for API requests
HEADERS = {
    "X-API-Key": API_KEY
}


def load_document(file_path: str) -> str:
    """
    Load document from file.
    
    Args:
        file_path: Path to document file
        
    Returns:
        Document content
    """
    with open(file_path, 'r') as f:
        return f.read()


def load_queries(file_path: str) -> List[str]:
    """
    Load queries from markdown file.
    
    Args:
        file_path: Path to queries file
        
    Returns:
        List of queries
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract queries (lines starting with '- ')
    queries = re.findall(r'^\s*-\s*(.*?)$', content, re.MULTILINE)
    
    return queries


def extract_text(text: str, query: str, domain: Optional[str] = None, use_parallel: bool = False) -> Dict[str, Any]:
    """
    Extract information from text using the API.
    
    This function sends a request to the /extract/text endpoint to extract
    information from the provided text based on the query. It can optionally
    use a specific domain and parallel extraction.
    
    Args:
        text: Text to extract from
        query: Query describing what to extract (e.g., "Extract patient information")
        domain: Optional domain to use for extraction (e.g., "medical", "legal")
        use_parallel: Whether to use parallel extraction for improved performance
        
    Returns:
        API response containing extraction results and metadata
        
    Example:
        result = extract_text(
            text="Patient: John Doe\nDOB: 05/15/1980",
            query="Extract patient information",
            domain="medical"
        )
    """
    url = f"{API_BASE_URL}/extract/text"
    
    # Prepare request data
    data = {
        "text": text,
        "query": query,
        "output_formats": ["json", "text"]
    }
    
    if domain:
        data["domain"] = domain
    
    # Add query parameter for parallel extraction
    params = {"use_parallel": "true" if use_parallel else "false"}
    
    # Send request
    response = requests.post(url, json=data, headers=HEADERS, params=params)
    
    # Check response
    if response.status_code == 200:
        return response.json()
    else:
        console.print(f"[bold red]Error: {response.status_code}[/]")
        console.print(response.text)
        return None


def extract_multi_query(text: str, queries: List[str], domain: Optional[str] = None, use_parallel: bool = False) -> Dict[str, Any]:
    """
    Extract information from text using multiple queries.
    
    This function sends a request to the /extract/multi-query endpoint to extract
    information from the provided text based on multiple queries. The results
    for each query are merged into a single response.
    
    Args:
        text: Text to extract from
        queries: List of queries describing what to extract
                (e.g., ["Extract patient information", "Extract diagnosis"])
        domain: Optional domain to use for extraction (e.g., "medical", "legal")
        use_parallel: Whether to use parallel extraction for improved performance
        
    Returns:
        API response containing extraction results for all queries
        
    Example:
        result = extract_multi_query(
            text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes",
            queries=["Extract patient information", "Extract diagnosis"],
            domain="medical"
        )
    """
    url = f"{API_BASE_URL}/extract/multi-query"
    
    # Prepare request data
    data = {
        "text": text,
        "queries": queries,
        "output_formats": ["json", "text"]
    }
    
    if domain:
        data["domain"] = domain
    
    # Add query parameter for parallel extraction
    params = {"use_parallel": "true" if use_parallel else "false"}
    
    # Send request
    response = requests.post(url, json=data, headers=HEADERS, params=params)
    
    # Check response
    if response.status_code == 200:
        return response.json()
    else:
        console.print(f"[bold red]Error: {response.status_code}[/]")
        console.print(response.text)
        return None


def extract_file(file_path: str, query: str, domain: Optional[str] = None, use_parallel: bool = False) -> Dict[str, Any]:
    """
    Extract information from file using the API.
    
    This function sends a request to the /extract/file endpoint to extract
    information from the provided file based on the query. The file is uploaded
    to the API server, which uses appropriate document loaders based on the file type.
    
    Args:
        file_path: Path to file (e.g., "data/legal_contract.txt")
        query: Query describing what to extract (e.g., "Extract all parties")
        domain: Optional domain to use for extraction (e.g., "medical", "legal")
        use_parallel: Whether to use parallel extraction for improved performance
        
    Returns:
        API response containing extraction results and metadata
        
    Example:
        result = extract_file(
            file_path="data/legal_contract.txt",
            query="Extract all parties involved in the contract",
            domain="legal"
        )
    """
    url = f"{API_BASE_URL}/extract/file"
    
    # Prepare request data
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "text/plain")
    }
    
    data = {
        "query": query,
        "output_formats": "json,text",
        "use_parallel": "true" if use_parallel else "false"
    }
    
    if domain:
        data["domain"] = domain
    
    # Send request
    response = requests.post(url, files=files, data=data, headers=HEADERS)
    
    # Check response
    if response.status_code == 200:
        return response.json()
    else:
        console.print(f"[bold red]Error: {response.status_code}[/]")
        console.print(response.text)
        return None


def extract_document(file_path: str, domain: str) -> Dict[str, Any]:
    """
    Extract all information from document using the API.
    
    This function sends a request to the /extract/document endpoint to extract
    all information from the provided file using the parallel extraction pipeline.
    This endpoint extracts all fields defined in the specified domain.
    
    Args:
        file_path: Path to file (e.g., "data/legal_contract.txt")
        domain: Domain to use for extraction (e.g., "medical", "legal")
        
    Returns:
        API response containing extraction results for all fields in the domain
        
    Example:
        result = extract_document(
            file_path="data/legal_contract.txt",
            domain="legal"
        )
    """
    url = f"{API_BASE_URL}/extract/document"
    
    # Prepare request data
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "text/plain")
    }
    
    data = {
        "domain": domain,
        "output_formats": "json,text"
    }
    
    # Send request
    response = requests.post(url, files=files, data=data, headers=HEADERS)
    
    # Check response
    if response.status_code == 200:
        return response.json()
    else:
        console.print(f"[bold red]Error: {response.status_code}[/]")
        console.print(response.text)
        return None


def display_extraction_result(result: Dict[str, Any]) -> None:
    """
    Display extraction result using rich formatting.
    
    This function formats and displays the extraction result using rich
    formatting for better readability. It shows the status, operation type,
    domain, fields, query, and extraction results.
    
    Args:
        result: Extraction result from the API
        
    Example:
        display_extraction_result(result)
    """
    # Display status
    status_color = "green" if result["status"] == "success" else "red"
    console.print(f"Status: [bold {status_color}]{result['status']}[/]")
    
    # Display operation type
    console.print(f"Operation Type: [cyan]{result['operation_type']}[/]")
    
    # Display domain and fields
    if "domain" in result and result["domain"]:
        console.print(f"Domain: [cyan]{result['domain']}[/]")
    
    if "fields" in result and result["fields"]:
        console.print(f"Fields: [cyan]{', '.join(result['fields'])}[/]")
    
    # Display query or queries
    if "query" in result and result["query"]:
        console.print(f"Query: [yellow]{result['query']}[/]")
    
    if "queries" in result and result["queries"]:
        console.print("Queries:")
        for query in result["queries"]:
            console.print(f"- [yellow]{query}[/]")
    
    # Display extraction result
    if "extraction_result" in result and result["extraction_result"]:
        console.print("\n[bold]Extraction Result:[/]")
        
        extraction_result = result["extraction_result"]
        
        if "json_output" in extraction_result and extraction_result["json_output"]:
            console.print("[cyan]JSON Output:[/]")
            console.print_json(data=extraction_result["json_output"])
        
        if "text_output" in extraction_result and extraction_result["text_output"]:
            console.print("[cyan]Text Output:[/]")
            console.print(Syntax(extraction_result["text_output"], "text"))
        
        if "metadata" in extraction_result and extraction_result["metadata"]:
            console.print("[cyan]Metadata:[/]")
            for key, value in extraction_result["metadata"].items():
                console.print(f"  [green]{key}:[/] {value}")
    
    # Display error message if any
    if "error_message" in result and result["error_message"]:
        console.print(f"[bold red]Error:[/] {result['error_message']}")


def main():
    """
    Main function that demonstrates different extraction scenarios.
    
    This function:
    1. Loads a document and queries from the data folder
    2. Demonstrates text extraction with a single query
    3. Demonstrates text extraction with multiple queries
    4. Demonstrates file extraction
    5. Demonstrates document extraction using parallel processing
    6. Demonstrates text extraction with parallel processing
    
    Each example shows how to call the API and display the results.
    """
    console.print(Panel("Dudoxx Extraction API Client Example", style="bold magenta"))
    
    # Load document and queries
    document_path = "data/legal_contract.txt"
    queries_path = "data/queries.md"
    
    console.print(f"Loading document from [cyan]{document_path}[/]")
    document_text = load_document(document_path)
    
    console.print(f"Loading queries from [cyan]{queries_path}[/]")
    queries = load_queries(queries_path)
    
    console.print(f"Loaded [green]{len(queries)}[/] queries")
    
    # Example 1: Extract information from text using a single query
    console.print(Panel("Example 1: Extract information from text using a single query", style="cyan"))
    
    query = queries[0]  # "Extract all parties involved in the contract"
    console.print(f"Query: [yellow]{query}[/]")
    
    result = extract_text(document_text, query, domain="legal")
    
    if result:
        display_extraction_result(result)
    
    # Example 2: Extract information from text using multiple queries
    console.print(Panel("Example 2: Extract information from text using multiple queries", style="cyan"))
    
    # Use first 3 legal document queries
    selected_queries = queries[:3]
    console.print(f"Queries: [yellow]{', '.join(selected_queries)}[/]")
    
    result = extract_multi_query(document_text, selected_queries, domain="legal")
    
    if result:
        display_extraction_result(result)
    
    # Example 3: Extract information from file
    console.print(Panel("Example 3: Extract information from file", style="cyan"))
    
    query = queries[3]  # "What are the termination conditions?"
    console.print(f"Query: [yellow]{query}[/]")
    
    result = extract_file(document_path, query, domain="legal")
    
    if result:
        display_extraction_result(result)
    
    # Example 4: Extract all information from document using parallel extraction
    console.print(Panel("Example 4: Extract all information from document using parallel extraction", style="cyan"))
    
    result = extract_document(document_path, domain="legal")
    
    if result:
        display_extraction_result(result)
    
    # Example 5: Extract information from text using parallel extraction
    console.print(Panel("Example 5: Extract information from text using parallel extraction", style="cyan"))
    
    query = queries[4]  # "Extract all legal obligations"
    console.print(f"Query: [yellow]{query}[/]")
    
    result = extract_text(document_text, query, domain="legal", use_parallel=True)
    
    if result:
        display_extraction_result(result)


if __name__ == "__main__":
    main()
