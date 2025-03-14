"""
Example of using the Parallel Extraction Pipeline.

This script demonstrates how to use the parallel extraction pipeline to extract
information from documents using multiple sub-domains in parallel.
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


def extract_from_medical_document():
    """Extract information from a medical document using the parallel extraction pipeline."""
    console = Console()
    console.print(Panel("Medical Document Extraction with Parallel Pipeline", style="green"))
    
    # Create example document if it doesn't exist
    example_dir = Path("examples")
    example_dir.mkdir(exist_ok=True)
    
    example_file = example_dir / "medical_record.txt"
    if not example_file.exists():
        console.print("Creating example medical document...")
        with open(example_file, "w") as f:
            f.write(MEDICAL_DOCUMENT)
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Get medical domain
    medical_domain = registry.get_domain("medical")
    if not medical_domain:
        console.print("[bold red]Error: Medical domain not found[/]")
        return
    
    # Print available sub-domains
    sub_domains_table = Table(title="Available Medical Sub-Domains")
    sub_domains_table.add_column("Name", style="cyan")
    sub_domains_table.add_column("Description", style="green")
    sub_domains_table.add_column("Fields", style="yellow")
    
    for sub_domain in medical_domain.sub_domains:
        sub_domains_table.add_row(
            sub_domain.name,
            sub_domain.description,
            ", ".join(sub_domain.get_field_names())
        )
    
    console.print(sub_domains_table)
    
    # Extract information using all sub-domains
    console.print("\n[bold]Extracting with all sub-domains...[/]")
    start_time = time.time()
    
    result = extract_document_sync(
        document_path=str(example_file),
        domain_name="medical",
        output_formats=["json", "text"]
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
    
    # Extract information using specific sub-domains
    console.print("\n[bold]Extracting with specific sub-domains...[/]")
    start_time = time.time()
    
    result = extract_document_sync(
        document_path=str(example_file),
        domain_name="medical",
        sub_domain_names=["patient_info", "medications", "diagnoses"],
        output_formats=["json", "text"]
    )
    
    total_time = time.time() - start_time
    
    # Print results
    console.print(f"\n[bold]Extraction completed in {total_time:.2f} seconds[/]")
    console.print(f"Chunk count: {result['metadata']['chunk_count']}")
    console.print(f"Sub-domain count: {result['metadata']['sub_domain_count']}")
    console.print(f"Task count: {result['metadata']['task_count']}")
    
    console.print("\n[bold]JSON Output (Selected Sub-Domains):[/]")
    json_str = json.dumps(result["json_output"], indent=2)
    console.print(Syntax(json_str, "json", theme="monokai", line_numbers=True))


def extract_from_legal_document():
    """Extract information from a legal document using the parallel extraction pipeline."""
    console = Console()
    console.print(Panel("Legal Document Extraction with Parallel Pipeline", style="blue"))
    
    # Create example document if it doesn't exist
    example_dir = Path("examples")
    example_dir.mkdir(exist_ok=True)
    
    example_file = example_dir / "legal_agreement.txt"
    if not example_file.exists():
        console.print("Creating example legal document...")
        with open(example_file, "w") as f:
            f.write(LEGAL_DOCUMENT)
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Get legal domain
    legal_domain = registry.get_domain("legal")
    if not legal_domain:
        console.print("[bold red]Error: Legal domain not found[/]")
        return
    
    # Print available sub-domains
    sub_domains_table = Table(title="Available Legal Sub-Domains")
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
    
    # Extract information using all sub-domains
    console.print("\n[bold]Extracting with all sub-domains...[/]")
    start_time = time.time()
    
    result = extract_document_sync(
        document_path=str(example_file),
        domain_name="legal",
        output_formats=["json", "text"]
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
    
    # Extract information using specific sub-domains
    console.print("\n[bold]Extracting with specific sub-domains...[/]")
    start_time = time.time()
    
    result = extract_document_sync(
        document_path=str(example_file),
        domain_name="legal",
        sub_domain_names=["agreement_info", "parties", "obligations"],
        output_formats=["json", "text"]
    )
    
    total_time = time.time() - start_time
    
    # Print results
    console.print(f"\n[bold]Extraction completed in {total_time:.2f} seconds[/]")
    console.print(f"Chunk count: {result['metadata']['chunk_count']}")
    console.print(f"Sub-domain count: {result['metadata']['sub_domain_count']}")
    console.print(f"Task count: {result['metadata']['task_count']}")
    
    console.print("\n[bold]JSON Output (Selected Sub-Domains):[/]")
    json_str = json.dumps(result["json_output"], indent=2)
    console.print(Syntax(json_str, "json", theme="monokai", line_numbers=True))


# Example medical document
MEDICAL_DOCUMENT = """
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

Insurance Information:
Provider: HealthCare Insurance
Policy Number: HCI-987654321
Group Number: GRP-123456

Medical History:
Allergies: Penicillin, Peanuts
Chronic Conditions: Type 2 Diabetes (diagnosed 2015), Hypertension (diagnosed 2018)
Previous Surgeries: Appendectomy (2010), Knee Arthroscopy (2019)
Family History: Father - Heart Disease, Mother - Breast Cancer

Current Medications:
1. Metformin 500mg, twice daily (for diabetes)
2. Lisinopril 10mg, once daily (for hypertension)
3. Aspirin 81mg, once daily (preventative)

Visit History:
-------------

Visit Date: 03/10/2023
Provider: Dr. Sarah Johnson
Chief Complaint: Persistent cough and fever
Vital Signs: BP 130/85, HR 88, Temp 100.2°F, RR 18, O2 Sat 97%
Assessment: Upper respiratory infection, likely viral
Plan: Rest, increased fluids, over-the-counter cough suppressant
Follow-up: As needed if symptoms worsen

Visit Date: 07/22/2023
Provider: Dr. Michael Chen
Chief Complaint: Routine diabetes check-up
Vital Signs: BP 128/82, HR 76, Temp 98.6°F, RR 16, O2 Sat 99%
Lab Results: HbA1c 7.1% (improved from 7.5%), Fasting glucose 135 mg/dL
Assessment: Type 2 Diabetes - well controlled
Plan: Continue current medications, maintain diet and exercise regimen
Follow-up: 3 months

Visit Date: 11/15/2023
Provider: Dr. Sarah Johnson
Chief Complaint: Annual physical examination
Vital Signs: BP 125/80, HR 72, Temp 98.4°F, RR 14, O2 Sat 99%
Lab Results: Comprehensive metabolic panel within normal limits, Lipid panel shows slightly elevated LDL (130 mg/dL)
Assessment: Overall good health, mild hyperlipidemia
Plan: Dietary modifications to reduce cholesterol, continue current medications
Follow-up: Annual physical in 1 year, diabetes check-up in 3 months
"""

# Example legal document
LEGAL_DOCUMENT = """
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


def main():
    """Main function."""
    # Extract from medical document
    extract_from_medical_document()
    
    # Extract from legal document
    # Create a small delay to ensure the previous asyncio event loop is properly closed
    import time
    time.sleep(1)
    
    extract_from_legal_document()


if __name__ == "__main__":
    main()
