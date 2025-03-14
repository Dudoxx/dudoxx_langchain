"""
Example of using the Legal Domain for extraction from legal documents.

This script demonstrates how to use the parallel extraction pipeline to extract
information from legal documents using specialized legal sub-domains.
"""

import os
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Add the project root to the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the parallel extraction pipeline
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync
from dudoxx_extraction.domains.domain_registry import DomainRegistry


def extract_from_legal_document(domain_name="legal", sub_domain_names=None):
    """
    Extract information from a legal document using the parallel extraction pipeline.
    
    Args:
        domain_name: Name of the domain to use (default: "legal")
        sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
    """
    console = Console()
    console.print(Panel(f"Legal Document Extraction: {domain_name}", style="blue"))
    
    # Use the legal contract from the data directory
    document_path = Path("data/legal_contract.txt")
    if not document_path.exists():
        console.print("[bold red]Error: Legal contract document not found at data/legal_contract.txt[/]")
        return
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Get legal domain
    legal_domain = registry.get_domain(domain_name)
    if not legal_domain:
        console.print(f"[bold red]Error: {domain_name} domain not found[/]")
        return
    
    # Print available sub-domains
    sub_domains_table = Table(title=f"Available {domain_name.replace('_', ' ').title()} Sub-Domains")
    sub_domains_table.add_column("Name", style="cyan")
    sub_domains_table.add_column("Description", style="green")
    sub_domains_table.add_column("Fields", style="yellow")
    
    for sub_domain in legal_domain.sub_domains:
        sub_domains_table.add_row(
            sub_domain.name,
            sub_domain.description,
            ", ".join(sub_domain.get_field_names())
        )
    
    console.print(sub_domains_table)
    
    # Extract information using specified sub-domains or all sub-domains
    if sub_domain_names:
        console.print(f"\n[bold]Extracting with specific sub-domains: {', '.join(sub_domain_names)}[/]")
    else:
        console.print("\n[bold]Extracting with all sub-domains[/]")
    
    start_time = time.time()
    
    # Process the document in chunks and extract information in parallel
    result = extract_document_sync(
        document_path=str(document_path),
        domain_name=domain_name,
        sub_domain_names=sub_domain_names,
        output_formats=["json", "text"],
        use_threads=True
    )
    
    total_time = time.time() - start_time
    
    # Print results
    console.print(f"\n[bold]Extraction completed in {total_time:.2f} seconds[/]")
    console.print(f"Chunk count: {result['metadata']['chunk_count']}")
    console.print(f"Sub-domain count: {result['metadata']['sub_domain_count']}")
    console.print(f"Task count: {result['metadata']['task_count']}")
    
    console.print("\n[bold]JSON Output:[/]")
    json_str = json.dumps(result["json_output"], indent=2)
    console.print(Syntax(json_str, "json", theme="monokai", line_numbers=True))
    
    console.print("\n[bold]Text Output:[/]")
    console.print(result["text_output"])


def extract_with_specialized_legal_domains():
    """
    Extract information from a legal document using specialized legal sub-domains.
    
    This function demonstrates how to extract specific types of information from
    legal documents by focusing on particular sub-domains.
    """
    console = Console()
    console.print(Panel("Specialized Legal Document Extraction", style="magenta"))
    
    # Extract contract information
    extract_from_legal_document(
        sub_domain_names=["agreement_info", "parties"]
    )
    
    # Extract financial terms
    console.print("\n[bold]Extracting financial and payment terms...[/]")
    extract_from_legal_document(
        sub_domain_names=["payment_terms"]
    )
    
    # Extract termination provisions
    console.print("\n[bold]Extracting termination provisions...[/]")
    extract_from_legal_document(
        sub_domain_names=["termination_provisions"]
    )


def main():
    """Main function."""
    # Extract from legal document with all sub-domains
    extract_from_legal_document()
    
    # Extract from legal document with specific sub-domains
    extract_from_legal_document(
        sub_domain_names=["agreement_info", "parties", "obligations", "confidentiality"]
    )
    
    # Demonstrate specialized extraction
    extract_with_specialized_legal_domains()


if __name__ == "__main__":
    main()
