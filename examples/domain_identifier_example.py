"""
Example of using the Domain Identifier component.

This script demonstrates how to use the Domain Identifier to identify appropriate
domains and fields for extraction based on raw text input.
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Domain Identifier
from dudoxx_extraction.domain_identifier import DomainIdentifier, DomainIdentifierTool, DomainIdentificationResult
from dudoxx_extraction.configuration_service import ConfigurationService
from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.client import ExtractionClientSync


def demonstrate_domain_identifier():
    """Demonstrate the use of the Domain Identifier."""
    console = Console()
    console.print(Panel("Domain Identifier Example", style="bold magenta"))
    
    # Display configuration information
    console.print(Panel("Configuration Information", style="green"))
    
    # Get LLM configuration
    config_service = ConfigurationService()
    llm_config = config_service.get_llm_config()
    
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
    
    # Create domain identifier
    console.print("\n[bold]Creating Domain Identifier...[/]")
    domain_identifier = DomainIdentifier()
    
    # Get available domains using the domain registry directly
    console.print("\n[bold]Retrieving available domains...[/]")
    try:
        # Get domain registry
        registry = DomainRegistry()
        
        # Log registered domains
        domain_names = registry.get_domain_names()
        console.print(f"Registered domains: {', '.join(domain_names)}")
        
        # Get all domains
        domains = registry.get_all_domains()
        
        # Create domain info structure manually
        domains_info = {"domains": [], "domain_count": len(domains)}
        
        for domain in domains:
            domain_info = {
                "name": domain.name,
                "description": domain.description,
                "sub_domains": []
            }
            
            for sub_domain in domain.sub_domains:
                sub_domain_info = {
                    "name": sub_domain.name,
                    "description": sub_domain.description,
                    "fields": []
                }
                
                for field in sub_domain.fields:
                    field_info = {
                        "name": field.name,
                        "description": field.description,
                        "type": field.type
                    }
                    sub_domain_info["fields"].append(field_info)
                
                domain_info["sub_domains"].append(sub_domain_info)
            
            domains_info["domains"].append(domain_info)
        
        # Display available domains
        domains_table = Table(title="Available Domains")
        domains_table.add_column("Domain", style="cyan")
        domains_table.add_column("Description", style="green")
        domains_table.add_column("Sub-Domains", style="yellow")
        domains_table.add_column("Fields", style="magenta")
        
        for domain_info in domains_info["domains"]:
            domain_name = domain_info["name"]
            domain_desc = domain_info["description"]
            
            # Get sub-domain names
            sub_domain_names = [sub_domain["name"] for sub_domain in domain_info["sub_domains"]]
            
            # Count total fields
            total_fields = sum(len(sub_domain["fields"]) for sub_domain in domain_info["sub_domains"])
            
            domains_table.add_row(
                domain_name,
                domain_desc,
                ", ".join(sub_domain_names),
                str(total_fields)
            )
        
        console.print(domains_table)
        
        # Display sub-domains for each domain
        for domain_info in domains_info["domains"]:
            domain_name = domain_info["name"]
            
            sub_domains_table = Table(title=f"Sub-Domains for {domain_name}")
            sub_domains_table.add_column("Sub-Domain", style="cyan")
            sub_domains_table.add_column("Description", style="green")
            sub_domains_table.add_column("Fields", style="yellow")
            
            for sub_domain in domain_info["sub_domains"]:
                sub_domain_name = sub_domain["name"]
                sub_domain_desc = sub_domain["description"]
                field_names = [field["name"] for field in sub_domain["fields"]]
                
                sub_domains_table.add_row(
                    sub_domain_name,
                    sub_domain_desc,
                    ", ".join(field_names)
                )
            
            console.print(sub_domains_table)
    except Exception as e:
        console.print(f"[bold red]Error retrieving domains: {e}[/]")
        console.print(f"[yellow]Traceback:[/] {e.__class__.__name__}: {str(e)}")
        
        # Fall back to using the domain registry directly
        registry = DomainRegistry()
        
        domains_table = Table(title="Available Domains (Fallback)")
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
    
    # Example 1: Medical text
    console.print(Panel("Example 1: Medical Text", style="cyan"))
    
    medical_text = """
    Patient Medical Record
    ----------------------

    Patient Information:
    Name: John Smith
    Date of Birth: 05/15/1980
    Gender: Male
    Medical Record Number: MRN-12345678

    Contact Information:
    Address: 123 Main Street, Anytown, CA 12345
    Phone: (555) 123-4567
    Email: john.smith@email.com
    Emergency Contact: Jane Smith (Wife), (555) 987-6543

    Medical History:
    Allergies: Penicillin, Peanuts
    Chronic Conditions: Type 2 Diabetes (diagnosed 2015), Hypertension (diagnosed 2018)
    Previous Surgeries: Appendectomy (2010), Knee Arthroscopy (2019)
    Family History: Father - Heart Disease, Mother - Breast Cancer

    Current Medications:
    1. Metformin 500mg, twice daily (for diabetes)
    2. Lisinopril 10mg, once daily (for hypertension)
    3. Aspirin 81mg, once daily (preventative)
    """
    
    console.print(Syntax(medical_text, "text", theme="monokai"))
    
    console.print("\n[bold]Identifying domains and fields...[/]")
    try:
        medical_result = domain_identifier.identify_domains_and_fields(medical_text)
        console.print("[bold green]✓[/] Domain identification successful")
    except Exception as e:
        console.print(f"[bold red]Error identifying domains and fields: {e}[/]")
        console.print(f"[yellow]Traceback:[/] {e.__class__.__name__}: {str(e)}")
        # Create empty result
        medical_result = DomainIdentificationResult(
            matched_domains=[],
            matched_sub_domains=[],
            matched_fields=[],
            recommended_domains=[],
            recommended_sub_domains={},
            recommended_fields={},
            text_summary="Error occurred during identification"
        )
    
    # Display results
    console.print("\n[bold]Recommended Domains:[/]")
    if medical_result.recommended_domains:
        for domain in medical_result.recommended_domains:
            console.print(f"- {domain}")
    else:
        console.print("[yellow]No domains recommended[/]")
    
    console.print("\n[bold]Recommended Sub-Domains:[/]")
    if medical_result.recommended_sub_domains:
        for domain, sub_domains in medical_result.recommended_sub_domains.items():
            console.print(f"- {domain}: {', '.join(sub_domains)}")
    else:
        console.print("[yellow]No sub-domains recommended[/]")
    
    console.print("\n[bold]Recommended Fields:[/]")
    if medical_result.recommended_fields:
        for key, fields in medical_result.recommended_fields.items():
            console.print(f"- {key}: {', '.join(fields)}")
    else:
        console.print("[yellow]No fields recommended[/]")
    
    # Display matched domains with confidence scores
    console.print("\n[bold]Matched Domains (with confidence):[/]")
    if medical_result.matched_domains:
        domains_matches_table = Table(title="Domain Matches")
        domains_matches_table.add_column("Domain", style="cyan")
        domains_matches_table.add_column("Confidence", style="green")
        domains_matches_table.add_column("Reason", style="yellow")
        
        for match in medical_result.matched_domains:
            domains_matches_table.add_row(
                match.domain_name,
                f"{match.confidence:.2f}",
                match.reason
            )
        
        console.print(domains_matches_table)
    else:
        console.print("[yellow]No domain matches found[/]")
    
    # Example 2: Legal text
    console.print(Panel("Example 2: Legal Text", style="cyan"))
    
    legal_text = """
    CONSULTING SERVICES AGREEMENT

    This Consulting Services Agreement (the "Agreement") is entered into as of January 15, 2023 (the "Effective Date") by and between:

    ABC Corporation, a Delaware corporation with its principal place of business at 123 Corporate Drive, Business City, CA 94123 ("Client")

    and

    XYZ Consulting LLC, a California limited liability company with its principal place of business at 456 Consultant Avenue, Expertise City, CA 95678 ("Consultant").

    WHEREAS, Client desires to retain Consultant to provide certain consulting services, and Consultant is willing to perform such services, under the terms and conditions set forth herein.

    NOW, THEREFORE, in consideration of the mutual covenants and agreements hereinafter set forth, the parties agree as follows:

    1. SERVICES

    1.1 Scope of Services. Consultant shall provide to Client the consulting services (the "Services") described in Exhibit A attached hereto and incorporated herein by reference.

    1.2 Performance of Services. Consultant shall perform the Services in accordance with the highest professional standards and shall comply with all applicable laws and regulations in the performance of the Services.

    2. TERM AND TERMINATION

    2.1 Term. This Agreement shall commence on the Effective Date and shall continue for a period of one (1) year, unless earlier terminated as provided herein (the "Term").

    2.2 Termination for Convenience. Either party may terminate this Agreement at any time without cause upon thirty (30) days' prior written notice to the other party.

    2.3 Termination for Cause. Either party may terminate this Agreement immediately upon written notice if the other party materially breaches this Agreement and fails to cure such breach within fifteen (15) days after receiving written notice thereof.

    3. COMPENSATION

    3.1 Fees. Client shall pay Consultant the fees set forth in Exhibit B attached hereto and incorporated herein by reference.

    3.2 Expenses. Client shall reimburse Consultant for all reasonable out-of-pocket expenses incurred by Consultant in connection with the performance of the Services, provided that such expenses are approved in advance by Client and Consultant submits appropriate documentation of such expenses.

    3.3 Invoicing and Payment. Consultant shall invoice Client monthly for fees and expenses. Client shall pay all undisputed amounts within thirty (30) days after receipt of each invoice.
    """
    
    console.print(Syntax(legal_text[:500] + "...", "text", theme="monokai"))
    
    console.print("\n[bold]Identifying domains and fields...[/]")
    try:
        legal_result = domain_identifier.identify_domains_and_fields(legal_text)
        console.print("[bold green]✓[/] Domain identification successful")
    except Exception as e:
        console.print(f"[bold red]Error identifying domains and fields: {e}[/]")
        console.print(f"[yellow]Traceback:[/] {e.__class__.__name__}: {str(e)}")
        # Create empty result
        legal_result = DomainIdentificationResult(
            matched_domains=[],
            matched_sub_domains=[],
            matched_fields=[],
            recommended_domains=[],
            recommended_sub_domains={},
            recommended_fields={},
            text_summary="Error occurred during identification"
        )
    
    # Display results
    console.print("\n[bold]Recommended Domains:[/]")
    if legal_result.recommended_domains:
        for domain in legal_result.recommended_domains:
            console.print(f"- {domain}")
    else:
        console.print("[yellow]No domains recommended[/]")
    
    console.print("\n[bold]Recommended Sub-Domains:[/]")
    if legal_result.recommended_sub_domains:
        for domain, sub_domains in legal_result.recommended_sub_domains.items():
            console.print(f"- {domain}: {', '.join(sub_domains)}")
    else:
        console.print("[yellow]No sub-domains recommended[/]")
    
    console.print("\n[bold]Recommended Fields:[/]")
    if legal_result.recommended_fields:
        for key, fields in legal_result.recommended_fields.items():
            console.print(f"- {key}: {', '.join(fields)}")
    else:
        console.print("[yellow]No fields recommended[/]")
    
    # Display matched domains with confidence scores
    console.print("\n[bold]Matched Domains (with confidence):[/]")
    if legal_result.matched_domains:
        domains_matches_table = Table(title="Domain Matches")
        domains_matches_table.add_column("Domain", style="cyan")
        domains_matches_table.add_column("Confidence", style="green")
        domains_matches_table.add_column("Reason", style="yellow")
        
        for match in legal_result.matched_domains:
            domains_matches_table.add_row(
                match.domain_name,
                f"{match.confidence:.2f}",
                match.reason
            )
        
        console.print(domains_matches_table)
    else:
        console.print("[yellow]No domain matches found[/]")
    
    # Example 3: Ambiguous text with mixed content
    console.print(Panel("Example 3: Ambiguous Text with Mixed Content", style="cyan"))
    
    mixed_text = """
    PATIENT AND LEGAL REPRESENTATIVE AGREEMENT

    Patient: Jane Doe
    Date of Birth: 10/25/1975
    Medical Record Number: MRN-87654321

    Legal Representative: John Doe (Spouse)
    Contact: (555) 987-6543

    This agreement is entered into on March 14, 2025, between Jane Doe ("Patient") and 
    Medical Center Inc., a healthcare provider located at 789 Health Avenue, Wellness City, CA 98765.

    The Patient hereby authorizes Medical Center Inc. to:
    1. Provide medical treatment as deemed necessary by healthcare professionals
    2. Release medical information to insurance providers for billing purposes
    3. Contact the designated legal representative in case of emergency

    Medical History Summary:
    - Hypertension (diagnosed 2018)
    - Allergies: Penicillin
    - Current Medications: Lisinopril 10mg daily

    Legal Terms:
    1. Term: This agreement shall remain in effect until terminated in writing by either party.
    2. Privacy: Medical Center Inc. shall maintain patient confidentiality in accordance with HIPAA regulations.
    3. Billing: Patient agrees to pay all charges not covered by insurance within 30 days of receipt of invoice.

    Signatures:
    Patient: _________________________ Date: _____________
    Medical Center Representative: _________________________ Date: _____________
    """
    
    console.print(Syntax(mixed_text, "text", theme="monokai"))
    
    console.print("\n[bold]Identifying domains and fields...[/]")
    try:
        mixed_result = domain_identifier.identify_domains_and_fields(mixed_text)
        console.print("[bold green]✓[/] Domain identification successful")
    except Exception as e:
        console.print(f"[bold red]Error identifying domains and fields: {e}[/]")
        console.print(f"[yellow]Traceback:[/] {e.__class__.__name__}: {str(e)}")
        # Create empty result
        mixed_result = DomainIdentificationResult(
            matched_domains=[],
            matched_sub_domains=[],
            matched_fields=[],
            recommended_domains=[],
            recommended_sub_domains={},
            recommended_fields={},
            text_summary="Error occurred during identification"
        )
    
    # Display results
    console.print("\n[bold]Recommended Domains:[/]")
    if mixed_result.recommended_domains:
        for domain in mixed_result.recommended_domains:
            console.print(f"- {domain}")
    else:
        console.print("[yellow]No domains recommended[/]")
    
    console.print("\n[bold]Recommended Sub-Domains:[/]")
    if mixed_result.recommended_sub_domains:
        for domain, sub_domains in mixed_result.recommended_sub_domains.items():
            console.print(f"- {domain}: {', '.join(sub_domains)}")
    else:
        console.print("[yellow]No sub-domains recommended[/]")
    
    console.print("\n[bold]Recommended Fields:[/]")
    if mixed_result.recommended_fields:
        for key, fields in mixed_result.recommended_fields.items():
            console.print(f"- {key}: {', '.join(fields)}")
    else:
        console.print("[yellow]No fields recommended[/]")
    
    # Display matched domains with confidence scores
    console.print("\n[bold]Matched Domains (with confidence):[/]")
    if mixed_result.matched_domains:
        domains_matches_table = Table(title="Domain Matches")
        domains_matches_table.add_column("Domain", style="cyan")
        domains_matches_table.add_column("Confidence", style="green")
        domains_matches_table.add_column("Reason", style="yellow")
        
        for match in mixed_result.matched_domains:
            domains_matches_table.add_row(
                match.domain_name,
                f"{match.confidence:.2f}",
                match.reason
            )
        
        console.print(domains_matches_table)
    else:
        console.print("[yellow]No domain matches found[/]")
    
    # Example 4: Using the Domain Identifier with the Extraction Client
    console.print(Panel("Example 4: Using Domain Identifier with Extraction Client", style="cyan"))
    
    # Create extraction client
    client = ExtractionClientSync()
    
    # Identify domains and fields
    console.print("\n[bold]Identifying domains and fields for medical text...[/]")
    try:
        medical_result = domain_identifier.identify_domains_and_fields(medical_text)
        console.print("[bold green]✓[/] Domain identification successful")
    except Exception as e:
        console.print(f"[bold red]Error identifying domains and fields: {e}[/]")
        console.print(f"[yellow]Traceback:[/] {e.__class__.__name__}: {str(e)}")
        # Create empty result
        medical_result = DomainIdentificationResult(
            matched_domains=[],
            matched_sub_domains=[],
            matched_fields=[],
            recommended_domains=[],
            recommended_sub_domains={},
            recommended_fields={},
            text_summary="Error occurred during identification"
        )
    
    # Get recommended domains and fields
    if medical_result.recommended_domains and "medical" in medical_result.recommended_domains:
        # Get recommended fields for medical domain
        fields = []
        for key, field_list in medical_result.recommended_fields.items():
            if key.startswith("medical."):
                fields.extend(field_list)
        
        if fields:
            console.print(f"\n[bold]Extracting fields: {', '.join(fields)}[/]")
            
            # Extract information
            extraction_result = client.extract_text(
                text=medical_text,
                fields=fields,
                domain="medical",
                output_formats=["json"]
            )
            
            # Display extraction result
            console.print("\n[bold]Extraction Result:[/]")
            json_str = json.dumps(extraction_result.get("json_output", {}), indent=2)
            console.print(Syntax(json_str, "json", theme="monokai"))
    
    console.print(Panel("Domain Identifier Example Completed", style="bold green"))


def main():
    """Main function."""
    demonstrate_domain_identifier()


if __name__ == "__main__":
    main()
