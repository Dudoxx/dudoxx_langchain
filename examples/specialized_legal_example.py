"""
Example of using the Specialized Legal Domains for extraction.

This script demonstrates how to use the parallel extraction pipeline with
specialized legal domains for detailed legal document analysis.
"""

import os
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Add the project root to the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the parallel extraction pipeline
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync
from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.configuration_service import ConfigurationService


def extract_from_specialized_legal_document(domain_name="specialized_legal", sub_domain_names=None):
    """
    Extract information from a legal document using specialized legal domains.
    
    Args:
        domain_name: Name of the domain to use (default: "specialized_legal")
        sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
    """
    console = Console()
    console.print(Panel(f"Specialized Legal Document Extraction: {domain_name}", style="magenta"))
    
    # Display configuration information
    console.print(Panel("Configuration Information", style="green"))
    
    # Get LLM and embedding configurations
    config_service = ConfigurationService()
    llm_config = config_service.get_llm_config()
    embedding_config = config_service.get_embedding_config()
    extraction_config = config_service.get_extraction_config()
    
    # Display LLM configuration
    llm_table = Table(title="LLM Configuration")
    llm_table.add_column("Setting", style="cyan")
    llm_table.add_column("Value", style="green")
    
    for key, value in llm_config.items():
        # Mask API key for security
        if key == "api_key" and value:
            masked_value = value[:4] + "..." + value[-4:]
            llm_table.add_row(key, masked_value)
        else:
            llm_table.add_row(key, str(value))
    
    console.print(llm_table)
    
    # Display embedding configuration
    embedding_table = Table(title="Embedding Configuration")
    embedding_table.add_column("Setting", style="cyan")
    embedding_table.add_column("Value", style="green")
    
    for key, value in embedding_config.items():
        # Mask API key for security
        if key == "api_key" and value:
            masked_value = value[:4] + "..." + value[-4:]
            embedding_table.add_row(key, masked_value)
        else:
            embedding_table.add_row(key, str(value))
    
    console.print(embedding_table)
    
    # Display extraction configuration
    extraction_table = Table(title="Extraction Configuration")
    extraction_table.add_column("Setting", style="cyan")
    extraction_table.add_column("Value", style="green")
    
    for key, value in extraction_config.items():
        extraction_table.add_row(key, str(value))
    
    console.print(extraction_table)
    
    # Use the legal contract from the data directory
    document_path = Path("data/legal_contract.txt")
    if not document_path.exists():
        console.print("[bold red]Error: Legal contract document not found at data/legal_contract.txt[/]")
        return
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Get specialized legal domain
    specialized_domain = registry.get_domain(domain_name)
    if not specialized_domain:
        console.print(f"[bold red]Error: {domain_name} domain not found[/]")
        return
    
    # Print available sub-domains
    sub_domains_table = Table(title=f"Available {domain_name.replace('_', ' ').title()} Sub-Domains")
    sub_domains_table.add_column("Name", style="cyan")
    sub_domains_table.add_column("Description", style="green")
    sub_domains_table.add_column("Fields", style="yellow")
    
    for sub_domain in specialized_domain.sub_domains:
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
    
    # Create a progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[cyan]{task.fields[status]}"),
        console=console
    ) as progress:
        # Add a task for extraction progress
        task = progress.add_task(
            f"[green]Extracting from {domain_name} domain...", 
            total=1,
            status="Processing"
        )
        
        # Process the document in chunks and extract information in parallel
        result = extract_document_sync(
            document_path=str(document_path),
            domain_name=domain_name,
            sub_domain_names=sub_domain_names,
            output_formats=["json", "text"],
            use_threads=True
        )
        
        # Update progress
        progress.update(task, completed=1, status="Completed")
    
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


def compare_legal_domains():
    """
    Compare extraction results between standard legal domain and specialized legal domain.
    
    This function demonstrates the differences in extraction capabilities between
    the standard legal domain and the more detailed specialized legal domain.
    """
    console = Console()
    console.print(Panel("Comparing Legal Domain Extraction Capabilities", style="yellow"))
    
    # Display configuration information
    config_service = ConfigurationService()
    llm_config = config_service.get_llm_config()
    
    # Display LLM configuration
    console.print(f"[bold]Using LLM:[/] {llm_config['model_name']} (Temperature: {llm_config['temperature']})")
    
    # Extract with standard legal domain
    console.print("\n[bold]Extracting with standard legal domain...[/]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[green]Processing with standard legal domain...", total=1)
        
        extract_document_sync(
            document_path="data/legal_contract.txt",
            domain_name="legal",
            sub_domain_names=["agreement_info", "parties"],
            output_formats=["json"],
            use_threads=True
        )
        
        progress.update(task, completed=1)
    
    # Create a small delay to ensure the previous extraction is properly completed
    time.sleep(1)
    
    # Extract with specialized legal domain
    console.print("\n[bold]Extracting with specialized legal domain...[/]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[green]Processing with specialized legal domain...", total=1)
        
        extract_document_sync(
            document_path="data/legal_contract.txt",
            domain_name="specialized_legal",
            sub_domain_names=["contract_info", "legal_representation"],
            output_formats=["json"],
            use_threads=True
        )
        
        progress.update(task, completed=1)


def extract_legal_fees_and_matter_details():
    """
    Extract legal fees and matter details from a legal document.
    
    This function demonstrates how to extract specific types of information
    from legal documents using specialized sub-domains.
    """
    console = Console()
    console.print(Panel("Extracting Legal Fees and Matter Details", style="cyan"))
    
    # Display configuration information
    config_service = ConfigurationService()
    llm_config = config_service.get_llm_config()
    embedding_config = config_service.get_embedding_config()
    
    # Display model information
    console.print(f"[bold]Using LLM:[/] {llm_config['model_name']}")
    console.print(f"[bold]Using Embeddings:[/] {embedding_config['model']}")
    
    # Extract legal fees
    console.print("\n[bold]Extracting legal fees information...[/]")
    extract_from_specialized_legal_document(
        sub_domain_names=["legal_fees"]
    )
    
    # Create a small delay to ensure the previous extraction is properly completed
    time.sleep(1)
    
    # Extract legal matter details
    console.print("\n[bold]Extracting legal matter details...[/]")
    extract_from_specialized_legal_document(
        sub_domain_names=["legal_matter"]
    )


def main():
    """Main function."""
    console = Console()
    console.print(Panel("Specialized Legal Document Extraction Demo", style="bold magenta"))
    
    # Display system information
    console.print("[bold]System Information:[/]")
    console.print(f"Python Version: {sys.version.split()[0]}")
    console.print(f"Rich Version: {Panel.__module__.split('.')[0]}")
    
    # Display configuration service information
    config_service = ConfigurationService()
    if config_service.validate_config():
        console.print("[bold green]✓[/] Configuration validated successfully")
    else:
        console.print("[bold red]✗[/] Configuration validation failed")
    
    # Extract from specialized legal document with all sub-domains
    extract_from_specialized_legal_document()
    
    # Extract from specialized legal document with specific sub-domains
    extract_from_specialized_legal_document(
        sub_domain_names=["contract_info", "legal_representation", "dispute_resolution"]
    )
    
    # Compare standard and specialized legal domains
    compare_legal_domains()
    
    # Extract specific legal information
    extract_legal_fees_and_matter_details()
    
    # Display summary
    console.print(Panel("Extraction Demo Completed", style="bold green"))


if __name__ == "__main__":
    main()
