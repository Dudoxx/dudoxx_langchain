#!/usr/bin/env python3
"""
Test script for the enhanced extraction system.

This script tests the enhanced domain definitions, function registry, and prompt builder
to ensure they work correctly with the extraction pipeline.
"""

import os
import json
from rich.console import Console
from rich.panel import Panel

# Import the enhanced components
from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.domains.medical_domain import register_medical_domain
from dudoxx_extraction.domains.legal_domain import register_legal_domain
from dudoxx_extraction.function_registry import FunctionRegistry
from dudoxx_extraction.prompt_builder import PromptBuilder
from dudoxx_extraction.extraction_pipeline import extract_text
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync


def test_prompt_builder():
    """Test the prompt builder with enhanced domain definitions."""
    console = Console()
    console.print(Panel.fit("Testing Prompt Builder", style="bold green"))
    
    # Register domains
    register_medical_domain()
    register_legal_domain()
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Create prompt builder
    prompt_builder = PromptBuilder(registry)
    
    # Sample text for testing
    sample_text = """
    PATIENT INFORMATION
    
    Name: John Smith
    DOB: 05/15/1980
    Gender: Male
    MRN: MRN-12345678
    
    ALLERGIES
    - Penicillin (severe rash)
    - Peanuts (anaphylaxis)
    
    MEDICATIONS
    - Metformin 500mg, twice daily (for diabetes)
    - Lisinopril 10mg, once daily (for hypertension)
    
    DIAGNOSES
    - Type 2 Diabetes Mellitus
    - Essential Hypertension
    - Hyperlipidemia
    """
    
    # Generate prompt for medical domain
    medical_prompt = prompt_builder.build_extraction_prompt(
        text=sample_text,
        domain_name="medical",
        field_names=["patient_name", "date_of_birth", "allergies", "medications"]
    )
    
    # Print the generated prompt
    console.print("Generated Medical Prompt:")
    console.print(medical_prompt)
    console.print()
    
    # Sample legal text
    legal_text = """
    AGREEMENT
    
    This Agreement is made and entered into as of January 1, 2023 (the "Effective Date"), by and between:
    
    Acme Corporation, a Delaware corporation with its principal place of business at 123 Main St, Anytown, USA ("Seller")
    
    and
    
    John Smith, an individual residing at 456 Oak Ave, Somewhere, USA ("Buyer")
    
    TERM
    
    This Agreement shall commence on the Effective Date and continue for a period of three (3) years, unless earlier terminated as provided herein.
    
    GOVERNING LAW
    
    This Agreement shall be governed by and construed in accordance with the laws of the State of California.
    """
    
    # Generate prompt for legal domain
    legal_prompt = prompt_builder.build_extraction_prompt(
        text=legal_text,
        domain_name="legal",
        field_names=["parties", "effective_date", "term_length", "governing_law"]
    )
    
    # Print the generated prompt
    console.print("Generated Legal Prompt:")
    console.print(legal_prompt)
    console.print()
    
    return True


def test_function_registry():
    """Test the function registry with some sample functions."""
    console = Console()
    console.print(Panel.fit("Testing Function Registry", style="bold green"))
    
    # Get function registry
    registry = FunctionRegistry()
    
    # Test date formatting function
    date_str = "05/15/1980"
    formatted_date = registry.call_function("format_date_iso", date_str)
    console.print(f"Original date: {date_str}")
    console.print(f"Formatted date (ISO): {formatted_date}")
    
    # Test name capitalization function
    name = "john smith"
    capitalized_name = registry.call_function("capitalize_names", name)
    console.print(f"Original name: {name}")
    console.print(f"Capitalized name: {capitalized_name}")
    
    # Test validation function
    email = "test@example.com"
    is_valid = registry.call_function("validate_email", email)
    console.print(f"Email: {email}")
    console.print(f"Is valid: {is_valid}")
    
    return True


def test_extraction_pipeline():
    """Test the extraction pipeline with enhanced domain definitions."""
    console = Console()
    console.print(Panel.fit("Testing Extraction Pipeline", style="bold green"))
    
    # Register domains
    register_medical_domain()
    register_legal_domain()
    
    # Sample text for testing
    sample_text = """
    PATIENT INFORMATION
    
    Name: John Smith
    DOB: 05/15/1980
    Gender: Male
    MRN: MRN-12345678
    
    ALLERGIES
    - Penicillin (severe rash)
    - Peanuts (anaphylaxis)
    
    MEDICATIONS
    - Metformin 500mg, twice daily (for diabetes)
    - Lisinopril 10mg, once daily (for hypertension)
    
    DIAGNOSES
    - Type 2 Diabetes Mellitus
    - Essential Hypertension
    - Hyperlipidemia
    """
    
    # Extract information using the extraction pipeline
    result = extract_text(
        text=sample_text,
        fields=["patient_name", "date_of_birth", "allergies", "medications"],
        domain="medical",
        output_formats=["json"]
    )
    
    # Print the extraction result
    console.print("Extraction Result:")
    console.print(json.dumps(result["json_output"], indent=2))
    console.print()
    
    return True


def test_file_extraction():
    """Test file extraction if a sample file is available."""
    console = Console()
    console.print(Panel.fit("Testing File Extraction", style="bold green"))
    
    # Check if sample files exist
    sample_files = [
        "data/legal_contract.txt",
        "examples/legal_agreement.txt",
        "examples/specialized_medical_record.txt"
    ]
    
    available_files = [f for f in sample_files if os.path.exists(f)]
    
    if not available_files:
        console.print("[yellow]No sample files found for testing file extraction.[/]")
        return False
    
    # Use the first available file
    sample_file = available_files[0]
    console.print(f"Using sample file: {sample_file}")
    
    # Determine domain based on filename
    domain = "legal" if "legal" in sample_file else "medical"
    
    # Determine fields based on domain
    fields = (
        ["parties", "effective_date", "termination_date", "governing_law"]
        if domain == "legal"
        else ["patient_name", "date_of_birth", "allergies", "medications"]
    )
    
    try:
        # Extract information from the file
        result = extract_document_sync(
            document_path=sample_file,
            domain_name=domain,
            output_formats=["json", "text"]
        )
        
        # Print the extraction result
        console.print("Extraction Result:")
        console.print(json.dumps(result["json_output"], indent=2))
        console.print()
        
        return True
    except Exception as e:
        console.print(f"[red]Error during file extraction: {e}[/]")
        return False


def main():
    """Run all tests."""
    console = Console()
    console.print(Panel.fit("Enhanced Extraction System Tests", style="bold blue"))
    
    # Run tests
    prompt_builder_result = test_prompt_builder()
    function_registry_result = test_function_registry()
    extraction_pipeline_result = test_extraction_pipeline()
    file_extraction_result = test_file_extraction()
    
    # Print summary
    console.print(Panel.fit("Test Results", style="bold blue"))
    console.print(f"Prompt Builder: {'✅' if prompt_builder_result else '❌'}")
    console.print(f"Function Registry: {'✅' if function_registry_result else '❌'}")
    console.print(f"Extraction Pipeline: {'✅' if extraction_pipeline_result else '❌'}")
    console.print(f"File Extraction: {'✅' if file_extraction_result else '❌'}")


if __name__ == "__main__":
    main()
