"""
Domain-based Extraction Example

This script demonstrates how to use the Domain Identifier to identify appropriate domains
and fields for extraction, and then use the Extraction Pipeline to extract the data.

The script:
1. Reads queries from a queries.md file in the data folder
2. Reads input text from the data folder
3. Performs domain identification using the improved domain identifier
4. Extracts data based on the identified domains using the extraction pipeline
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import required components
from dudoxx_extraction.domain_identifier import DomainIdentifier
from dudoxx_extraction.extraction_pipeline import extract_file
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def parse_queries_file(file_path: str) -> List[str]:
    """
    Parse queries from a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        List of queries
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract queries (lines starting with '- ')
    queries = re.findall(r'^\s*-\s*(.*?)$', content, re.MULTILINE)
    
    return queries


def get_domain_and_fields(query: str, domain_identifier: DomainIdentifier) -> Tuple[str, List[str]]:
    """
    Get the domain and fields for a query using the domain identifier.
    
    Args:
        query: Query to identify domains and fields for
        domain_identifier: Domain identifier instance
        
    Returns:
        Tuple of (domain, fields)
    """
    # Get extraction schema
    extraction_schema = domain_identifier.get_extraction_schema(query)
    
    # Get the primary domain (first domain in the schema)
    if not extraction_schema:
        return None, []
    
    primary_domain = next(iter(extraction_schema.keys()))
    
    # Get fields from all subdomains in the primary domain
    fields = []
    for subdomain, field_list in extraction_schema[primary_domain].items():
        for field_name, confidence in field_list:
            fields.append(field_name)
    
    return primary_domain, fields


def extract_data(document_path: str, query: str, domain_identifier: DomainIdentifier) -> Dict[str, Any]:
    """
    Extract data from a document based on a query.
    
    Args:
        document_path: Path to the document
        query: Query to extract data for
        domain_identifier: Domain identifier instance
        
    Returns:
        Extraction results
    """
    # Get domain and fields
    domain, fields = get_domain_and_fields(query, domain_identifier)
    
    if not domain or not fields:
        return {
            "error": "Could not identify domain or fields for query",
            "query": query
        }
    
    # Extract data
    result = extract_file(
        file_path=document_path,
        fields=fields,
        domain=domain,
        output_formats=["json", "text"]
    )
    
    # Add query and domain information
    result["query"] = query
    result["domain"] = domain
    result["fields"] = fields
    
    return result


def display_results(result: Dict[str, Any], console: Console) -> None:
    """
    Display extraction results using rich formatting.
    
    Args:
        result: Extraction result
        console: Rich console
    """
    # Display query information
    console.print(Panel(f"Query: {result['query']}", style="bold magenta"))
    
    # Check if there was an error
    if "error" in result:
        console.print(f"[bold red]Error:[/] {result['error']}")
        console.print("\n" + "="*80 + "\n")
        return
    
    # Display domain and fields information
    console.print(f"Domain: [cyan]{result['domain']}[/]")
    console.print(f"Fields: [green]{', '.join(result['fields'])}[/]")
    
    # Display extraction results
    console.print("\n[bold]Extraction Results:[/]")
    
    if "json_output" in result:
        # Create a table for the results
        results_table = Table(title="Extracted Data")
        results_table.add_column("Field", style="cyan")
        results_table.add_column("Value", style="yellow")
        
        for field, value in result["json_output"].items():
            if isinstance(value, list):
                if value and all(isinstance(item, dict) for item in value):
                    # Format list of dictionaries
                    formatted_value = "\n".join([
                        ", ".join([f"{k}: {v}" for k, v in item.items()])
                        for item in value
                    ])
                else:
                    # Format list of values
                    formatted_value = ", ".join([str(item) for item in value]) if value else "None"
            elif isinstance(value, dict):
                # Format dictionary
                formatted_value = "\n".join([f"{k}: {v}" for k, v in value.items()])
            else:
                # Format simple value
                formatted_value = str(value) if value is not None else "None"
            
            results_table.add_row(field, formatted_value)
        
        console.print(results_table)
    
    # Display metadata
    if "metadata" in result:
        console.print("\n[bold]Metadata:[/]")
        console.print(f"Processing time: [green]{result['metadata']['processing_time']:.2f}[/] seconds")
        console.print(f"Token count: [green]{result['metadata']['token_count']}[/]")
    
    console.print("\n" + "="*80 + "\n")


def main():
    """Main function to run the domain-based extraction example."""
    console = Console()
    
    # Initialize domain identifier
    domain_identifier = DomainIdentifier(use_rich_logging=True)
    
    # Get queries
    queries_file = os.path.join(project_root, "data", "queries.md")
    queries = parse_queries_file(queries_file)
    
    # Get document path
    document_path = os.path.join(project_root, "data", "legal_contract.txt")
    
    console.print(Panel("Domain-based Extraction Example", style="bold green"))
    console.print(f"Document: [cyan]{document_path}[/]")
    console.print(f"Queries: [cyan]{len(queries)}[/] queries from {queries_file}\n")
    
    # Process each query
    for i, query in enumerate(queries, 1):
        console.print(f"[bold]Processing query {i}/{len(queries)}[/]")
        
        # Extract data
        result = extract_data(document_path, query, domain_identifier)
        
        # Display results
        display_results(result, console)


if __name__ == "__main__":
    main()
