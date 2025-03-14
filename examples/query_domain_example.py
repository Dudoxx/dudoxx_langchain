"""
Example of using the Domain Identifier with user queries.

This script demonstrates how to use the Domain Identifier to identify appropriate
domains and fields for extraction based on natural language queries.
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Domain Identifier
from dudoxx_extraction.domain_identifier import DomainIdentifier
from dudoxx_extraction.domains.domain_registry import DomainRegistry


def demonstrate_query_domain_identification():
    """Demonstrate the use of the Domain Identifier with user queries."""
    console = Console()
    console.print(Panel("Domain Identifier Query Example", style="bold magenta"))
    
    # Create domain identifier
    console.print("\n[bold]Creating Domain Identifier...[/]")
    domain_identifier = DomainIdentifier()
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Log registered domains
    domain_names = registry.get_domain_names()
    console.print(f"Registered domains: {', '.join(domain_names)}")
    
    # Display available domains
    domains_table = Table(title="Available Domains")
    domains_table.add_column("Domain", style="cyan")
    domains_table.add_column("Description", style="green")
    domains_table.add_column("Sub-Domains", style="yellow")
    
    for domain in registry.get_all_domains():
        sub_domain_names = [sub_domain.name for sub_domain in domain.sub_domains]
        domains_table.add_row(
            domain.name,
            domain.description,
            ", ".join(sub_domain_names)
        )
    
    console.print(domains_table)
    
    # Example queries
    example_queries = [
        "What are the patient information?",
        "Show me the contract details",
        "Get the medical history",
        "What are the party names in the agreement?",
        "Find the patient's allergies",
        "What medications is the patient taking?",
        "Who are the parties in this contract?",
        "What is the effective date of the agreement?",
        "Show me the patient's contact information"
    ]
    
    # Process each query
    for query in example_queries:
        console.print(Panel(f"Query: {query}", style="cyan"))
        
        # Identify domains and fields
        result = domain_identifier.identify_domains_for_query(query)
        
        # Display matched domains
        console.print("\n[bold]Matched Domains:[/]")
        if result.matched_domains:
            domains_matches_table = Table(title="Domain Matches")
            domains_matches_table.add_column("Domain", style="cyan")
            domains_matches_table.add_column("Confidence", style="green")
            domains_matches_table.add_column("Reason", style="yellow")
            
            for match in result.matched_domains:
                domains_matches_table.add_row(
                    match.domain_name,
                    f"{match.confidence:.2f}",
                    match.reason
                )
            
            console.print(domains_matches_table)
        else:
            console.print("[yellow]No domain matches found[/]")
        
        # Display matched fields
        console.print("\n[bold]Matched Fields:[/]")
        if result.matched_fields:
            fields_matches_table = Table(title="Field Matches")
            fields_matches_table.add_column("Domain", style="cyan")
            fields_matches_table.add_column("Sub-Domain", style="green")
            fields_matches_table.add_column("Field", style="yellow")
            fields_matches_table.add_column("Confidence", style="magenta")
            fields_matches_table.add_column("Reason", style="blue")
            
            for match in result.matched_fields:
                fields_matches_table.add_row(
                    match.domain_name,
                    match.sub_domain_name,
                    match.field_name,
                    f"{match.confidence:.2f}",
                    match.reason
                )
            
            console.print(fields_matches_table)
        else:
            console.print("[yellow]No field matches found[/]")
        
        # Display recommendations
        console.print("\n[bold]Recommendations:[/]")
        console.print(f"Recommended domains: {', '.join(result.recommended_domains)}")
        
        for domain, fields in result.recommended_fields.items():
            console.print(f"Recommended fields for {domain}: {', '.join(fields)}")
        
        # Create a summary table for the identified domains and fields
        summary_table = Table(title=f"[bold]Summary for Query: {query}[/]", border_style="green")
        summary_table.add_column("Domain", style="cyan")
        summary_table.add_column("Sub-Domain", style="green")
        summary_table.add_column("Field", style="yellow")
        summary_table.add_column("Type", style="magenta")
        summary_table.add_column("Confidence", style="blue")
        
        # Add rows for each recommended field
        for domain_name, fields in result.recommended_fields.items():
            domain_obj = registry.get_domain(domain_name)
            if domain_obj:
                for field_path in fields:
                    # Parse field path (format: sub_domain.field)
                    parts = field_path.split('.')
                    if len(parts) == 2:
                        sub_domain_name, field_name = parts
                        
                        # Get sub-domain
                        sub_domain = domain_obj.get_sub_domain(sub_domain_name)
                        
                        if sub_domain:
                            # Find field
                            field_type = ""
                            confidence = 0.0
                            
                            for field in sub_domain.fields:
                                if field.name == field_name:
                                    field_type = field.type
                                    break
                            
                            # Find confidence from matched fields
                            for match in result.matched_fields:
                                if (match.domain_name == domain_name and 
                                    match.sub_domain_name == sub_domain_name and 
                                    match.field_name == field_name):
                                    confidence = match.confidence
                                    break
                            
                            summary_table.add_row(
                                domain_name,
                                sub_domain_name,
                                field_name,
                                field_type,
                                f"{confidence:.2f}" if confidence > 0 else "N/A"
                            )
        
        console.print(summary_table)
        
        # Test domain instantiation for each identified domain and fields
        console.print("\n[bold]Domain Instantiation Test:[/]")
        
        for domain_name in result.recommended_domains:
            # Get domain from registry
            domain_obj = registry.get_domain(domain_name)
            
            if domain_obj:
                console.print(f"[green]✓[/] Successfully instantiated domain: [cyan]{domain_name}[/]")
                
                # Check if the domain has the recommended fields
                if domain_name in result.recommended_fields:
                    field_validation_table = Table(title=f"Field Validation for {domain_name}")
                    field_validation_table.add_column("Field", style="cyan")
                    field_validation_table.add_column("Sub-Domain", style="green")
                    field_validation_table.add_column("Status", style="yellow")
                    field_validation_table.add_column("Type", style="magenta")
                    
                    for field_path in result.recommended_fields[domain_name]:
                        # Parse field path (format: sub_domain.field)
                        parts = field_path.split('.')
                        if len(parts) == 2:
                            sub_domain_name, field_name = parts
                            
                            # Get sub-domain
                            sub_domain = domain_obj.get_sub_domain(sub_domain_name)
                            
                            if sub_domain:
                                # Check if field exists in sub-domain
                                field_exists = False
                                field_type = ""
                                
                                for field in sub_domain.fields:
                                    if field.name == field_name:
                                        field_exists = True
                                        field_type = field.type
                                        break
                                
                                if field_exists:
                                    field_validation_table.add_row(
                                        field_name,
                                        sub_domain_name,
                                        "[green]✓ Found[/]",
                                        field_type
                                    )
                                else:
                                    field_validation_table.add_row(
                                        field_name,
                                        sub_domain_name,
                                        "[red]✗ Not Found[/]",
                                        ""
                                    )
                            else:
                                field_validation_table.add_row(
                                    field_name,
                                    sub_domain_name,
                                    "[red]✗ Sub-Domain Not Found[/]",
                                    ""
                                )
                    
                    console.print(field_validation_table)
            else:
                console.print(f"[red]✗[/] Failed to instantiate domain: [cyan]{domain_name}[/]")
        
        # Create a recap for this query
        console.print(Panel(f"Recap for Query: {query}", style="bold green"))
        
        # Sort domains by confidence
        sorted_domains = sorted(
            [(match.domain_name, match.confidence) for match in result.matched_domains],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Display highest rated domains for this query
        if sorted_domains:
            domains_recap_table = Table(title="Highest Rated Domains for this Query")
            domains_recap_table.add_column("Domain", style="cyan")
            domains_recap_table.add_column("Confidence", style="green")
            
            for domain_name, confidence in sorted_domains:
                domains_recap_table.add_row(
                    domain_name,
                    f"{confidence:.2f}"
                )
            
            console.print(domains_recap_table)
        
        # Sort fields by confidence
        sorted_fields = sorted(
            [(match.domain_name, match.sub_domain_name, match.field_name, match.confidence) 
             for match in result.matched_fields],
            key=lambda x: x[3],
            reverse=True
        )
        
        # Display highest rated fields for this query
        if sorted_fields:
            fields_recap_table = Table(title="Highest Rated Fields for this Query")
            fields_recap_table.add_column("Domain", style="cyan")
            fields_recap_table.add_column("Sub-Domain", style="green")
            fields_recap_table.add_column("Field", style="yellow")
            fields_recap_table.add_column("Confidence", style="magenta")
            
            for domain_name, sub_domain_name, field_name, confidence in sorted_fields[:10]:  # Show top 10 fields
                fields_recap_table.add_row(
                    domain_name,
                    sub_domain_name,
                    field_name,
                    f"{confidence:.2f}"
                )
            
            console.print(fields_recap_table)
        
        # Create a recommended extraction schema for this query
        console.print("[bold]Recommended Extraction Schema for this Query:[/]")
        
        # Get top domains (confidence > 0.7)
        top_domains = [domain for domain, confidence in sorted_domains if confidence > 0.7]
        
        # Get top fields for each domain (confidence > 0.7)
        extraction_schema = {}
        for domain_name, sub_domain_name, field_name, confidence in sorted_fields:
            if confidence > 0.7:
                if domain_name in top_domains:
                    if domain_name not in extraction_schema:
                        extraction_schema[domain_name] = {}
                    
                    if sub_domain_name not in extraction_schema[domain_name]:
                        extraction_schema[domain_name][sub_domain_name] = []
                    
                    extraction_schema[domain_name][sub_domain_name].append((field_name, confidence))
        
        # Display extraction schema
        for domain_name, sub_domains in extraction_schema.items():
            console.print(f"[bold cyan]{domain_name}[/]")
            
            for sub_domain_name, fields in sub_domains.items():
                console.print(f"  [green]{sub_domain_name}[/]")
                
                # Sort fields by confidence
                sorted_sub_fields = sorted(fields, key=lambda x: x[1], reverse=True)
                
                for field_name, confidence in sorted_sub_fields:
                    console.print(f"    [yellow]{field_name}[/] ([magenta]{confidence:.2f}[/])")
        
        console.print("\n" + "-" * 80 + "\n")
    
    console.print(Panel("Domain Identifier Query Example Completed", style="bold green"))


def main():
    """Main function."""
    demonstrate_query_domain_identification()


if __name__ == "__main__":
    main()
