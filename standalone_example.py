"""
Standalone Example of the Automated Large-Text Field Extraction Solution

This script demonstrates how to use the extraction functionality without relying on the package structure.
It can be easily copied into a bigger project.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env file and override existing environment variables
load_dotenv(override=True)

# Get OpenAI settings from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize OpenAI client
try:
    # Try to import from langchain_openai (recommended)
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fall back to langchain_community if langchain_openai is not installed
    from langchain_community.chat_models import ChatOpenAI
    print("Warning: Using deprecated ChatOpenAI from langchain_community.")
    print("Consider installing langchain_openai: pip install langchain_openai")

# Import other required components
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def extract_text(text: str, fields: List[str], domain: str, output_formats: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract information from text using OpenAI LLM.
    
    Args:
        text: Text to extract information from
        fields: List of fields to extract
        domain: Domain context (e.g., "medical", "legal")
        output_formats: List of output formats (e.g., ["json", "text"])
        
    Returns:
        Dictionary with extraction results
    """
    if output_formats is None:
        output_formats = ["json", "text"]
    
    start_time = time.time()
    
    # Initialize ChatOpenAI with settings from .env
    llm = ChatOpenAI(
        model_name=OPENAI_MODEL_NAME,
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_BASE_URL
    )
    
    # Create field descriptions based on domain
    field_descriptions = {
        "patient_name": "Full name of the patient",
        "date_of_birth": "Patient's date of birth",
        "gender": "Patient's gender",
        "medical_record_number": "Medical record number",
        "allergies": "List of patient allergies",
        "chronic_conditions": "List of chronic conditions",
        "medications": "List of current medications",
        "diagnoses": "List of diagnoses",
        "visits": "List of medical visits with dates and descriptions",
        "parties": "Parties involved in the contract",
        "effective_date": "Date when the contract becomes effective",
        "termination_date": "Date when the contract terminates",
        "obligations": "List of obligations for each party",
        "events": "List of events with dates and descriptions"
    }
    
    # Create field list for prompt
    field_list = "\n".join([f"- {field}: {field_descriptions.get(field, '')}" for field in fields])
    
    # Create prompt
    prompt_template = f"""Extract the following information from the {domain} document:

{field_list}

Return the information in JSON format with the field names as keys.
If a field is not found in the text, return null for that field.
If a field can have multiple values, return them as a list.

Text:
{{text}}
"""
    
    # Create prompt template
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create parser
    parser = JsonOutputParser()
    
    # Create chain
    chain = prompt | llm | parser
    
    # Extract information
    json_output = chain.invoke({"text": text})
    
    # Create text output
    text_output = ""
    for field, value in json_output.items():
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                # Handle list of dictionaries (e.g., visits)
                text_output += f"\n{field.replace('_', ' ').title()}:\n"
                for item in value:
                    item_str = ", ".join([f"{k}: {v}" for k, v in item.items()])
                    text_output += f"- {item_str}\n"
            else:
                # Handle list of strings
                text_output += f"{field.replace('_', ' ').title()}: {', '.join(value)}\n"
        elif isinstance(value, dict):
            # Handle dictionary
            text_output += f"{field.replace('_', ' ').title()}:\n"
            for k, v in value.items():
                text_output += f"- {k}: {v}\n"
        else:
            # Handle simple value
            text_output += f"{field.replace('_', ' ').title()}: {value}\n"
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Create result
    result = {
        "json_output": json_output,
        "text_output": text_output,
        "metadata": {
            "processing_time": processing_time,
            "chunk_count": 1,
            "token_count": len(text) // 4  # Rough estimate
        }
    }
    
    return result


def extract_file(file_path: str, fields: List[str], domain: str, output_formats: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract information from a file.
    
    Args:
        file_path: Path to the file
        fields: List of fields to extract
        domain: Domain context (e.g., "medical", "legal")
        output_formats: List of output formats (e.g., ["json", "text"])
        
    Returns:
        Dictionary with extraction results
    """
    # Just call extract_text with the file contents
    with open(file_path, "r") as f:
        text = f.read()
    
    return extract_text(text, fields, domain, output_formats)


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


def main():
    """Main function."""
    print("\n=== Medical Document Extraction ===\n")
    
    # Define fields to extract
    fields = ["patient_name", "date_of_birth", "diagnoses", "medications", "visits"]
    
    # Extract information
    result = extract_text(
        text=MEDICAL_DOCUMENT,
        fields=fields,
        domain="medical",
        output_formats=["json", "text"]
    )
    
    # Print results
    print("JSON Output:")
    print(json.dumps(result.get("json_output", {}), indent=2))
    
    print("\nText Output:")
    print(result.get("text_output", ""))
    
    print(f"\nProcessing Time: {result.get('metadata', {}).get('processing_time', 0):.2f} seconds")
    print(f"Chunk Count: {result.get('metadata', {}).get('chunk_count', 0)}")
    print(f"Token Count: {result.get('metadata', {}).get('token_count', 0)}")


if __name__ == "__main__":
    main()
