"""
Example of using the Query Preprocessor to improve extraction.

This script demonstrates how the Query Preprocessor can be used to analyze and
reformulate user queries for better domain and field identification.
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Query Preprocessor and Domain Identifier
from dudoxx_extraction.query_preprocessor import QueryPreprocessor
from dudoxx_extraction.domain_identifier import DomainIdentifier
from dudoxx_extraction.extraction_pipeline import extract_text
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync


def demonstrate_query_preprocessing():
    """Demonstrate the use of the Query Preprocessor with various queries."""
    console = Console()
    console.print(Panel("Query Preprocessor Example", style="bold magenta"))
    
    # Create query preprocessor
    console.print("\n[bold]Creating Query Preprocessor...[/]")
    query_preprocessor = QueryPreprocessor()
    
    # Example queries
    example_queries = [
        "What is the patient's name and date of birth?",
        "Extract all parties involved in the contract, the effective date, and any termination provisions.",
        "I need to find all allergies and medications from this medical record.",
        "Show me the patient's contact information and medical history.",
        "What are the key terms and conditions in this legal agreement?",
        "Extract demographic information from this document."
    ]
    
    # Process each query
    for query in example_queries:
        console.print(Panel(f"Original Query: {query}", style="cyan"))
        
        # Preprocess the query
        preprocessed_query = query_preprocessor.preprocess_query(query)
        
        # Display the preprocessed query
        console.print(Panel(f"Reformulated Query: {preprocessed_query.reformulated_query}", style="green"))
        
        # Display identified domain and fields
        if preprocessed_query.identified_domain:
            console.print(f"Identified Domain: [bold cyan]{preprocessed_query.identified_domain}[/]")
        else:
            console.print("[yellow]No domain identified[/]")
        
        if preprocessed_query.identified_fields:
            console.print("Identified Fields:")
            for field in preprocessed_query.identified_fields:
                console.print(f"  - [bold green]{field}[/]")
        else:
            console.print("[yellow]No fields identified[/]")
        
        # Display extraction requirements
        if preprocessed_query.extraction_requirements:
            console.print("Extraction Requirements:")
            for requirement, description in preprocessed_query.extraction_requirements.items():
                console.print(f"  - [bold yellow]{requirement}[/]: {description}")
        
        # Display confidence
        console.print(f"Confidence: [bold magenta]{preprocessed_query.confidence:.2f}[/]")
        
        # Compare with domain identifier
        console.print("\n[bold]Comparing with Domain Identifier...[/]")
        domain_identifier = DomainIdentifier(use_query_preprocessor=False)
        extraction_schema = domain_identifier.get_extraction_schema(query)
        
        # Display extraction schema
        console.print("Extraction Schema from Domain Identifier:")
        for domain_name, sub_domains in extraction_schema.items():
            console.print(f"  Domain: [bold cyan]{domain_name}[/]")
            for sub_domain_name, fields in sub_domains.items():
                console.print(f"    Sub-domain: [bold green]{sub_domain_name}[/]")
                for field_name, confidence in fields:
                    console.print(f"      Field: [bold yellow]{field_name}[/] (Confidence: {confidence:.2f})")
        
        console.print("\n" + "-" * 80 + "\n")


def demonstrate_extraction_with_preprocessing():
    """Demonstrate extraction with and without query preprocessing."""
    console = Console()
    console.print(Panel("Extraction with Query Preprocessing Example", style="bold blue"))
    
    # Example text
    example_text = """
    PATIENT INFORMATION
    
    Name: John Smith
    Date of Birth: 05/15/1980
    Gender: Male
    Medical Record Number: MRN12345
    
    ALLERGIES
    - Penicillin (Severe - Anaphylaxis)
    - Peanuts (Moderate - Hives)
    
    MEDICATIONS
    1. Lisinopril 10mg daily for hypertension
    2. Metformin 500mg twice daily for diabetes
    3. Atorvastatin 20mg daily for high cholesterol
    
    MEDICAL HISTORY
    Patient has a history of Type 2 Diabetes diagnosed in 2015, Hypertension since 2018,
    and underwent appendectomy in 2010. Family history significant for heart disease and diabetes.
    
    RECENT VISIT: 03/10/2023
    Chief Complaint: Persistent cough and fever for 5 days
    Vital Signs: BP 130/85, HR 88, Temp 100.2°F
    Assessment: Acute bronchitis
    Plan: Prescribed azithromycin 500mg on day 1, then 250mg daily for 4 days. Follow up in 1 week if symptoms persist.
    """
    
    # Example query
    query = "What medications is the patient taking and what allergies do they have?"
    
    console.print(f"\n[bold]Query:[/] {query}")
    console.print("\n[bold]Example Text:[/]")
    console.print(example_text[:200] + "...")  # Show just the beginning
    
    # Extract without preprocessing
    console.print("\n[bold]Extracting without Query Preprocessing...[/]")
    result_without_preprocessing = extract_text(
        text=example_text,
        fields=["medications", "allergies"],
        domain="medical",
        use_query_preprocessor=False
    )
    
    # Extract with preprocessing
    console.print("\n[bold]Extracting with Query Preprocessing...[/]")
    result_with_preprocessing = extract_text(
        text=example_text,
        fields=["medications", "allergies"],
        domain="medical",
        use_query_preprocessor=True
    )
    
    # Compare results
    console.print("\n[bold]Comparing Results:[/]")
    
    # Display results without preprocessing
    console.print(Panel("Results without Preprocessing", style="yellow"))
    console.print(result_without_preprocessing["text_output"])
    
    # Display results with preprocessing
    console.print(Panel("Results with Preprocessing", style="green"))
    console.print(result_with_preprocessing["text_output"])
    
    # Compare processing time
    time_without = result_without_preprocessing["metadata"]["processing_time"]
    time_with = result_with_preprocessing["metadata"]["processing_time"]
    
    console.print(f"\nProcessing time without preprocessing: [yellow]{time_without:.2f}[/] seconds")
    console.print(f"Processing time with preprocessing: [green]{time_with:.2f}[/] seconds")
    
    # Calculate improvement
    if time_without > 0:
        improvement = ((time_without - time_with) / time_without) * 100
        console.print(f"Improvement: [bold]{'%.2f' % improvement}%[/]")


def main():
    """Main function."""
    console = Console()
    
    # Demonstrate query preprocessing
    demonstrate_query_preprocessing()
    
    # Demonstrate extraction with preprocessing
    demonstrate_extraction_with_preprocessing()
    
    console.print(Panel("Query Preprocessing Example Completed", style="bold green"))


if __name__ == "__main__":
    main()
