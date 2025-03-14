"""
Example of using PydanticOutputParser with the Extraction Pipeline

This module demonstrates how to use PydanticOutputParser to get structured outputs
from the extraction pipeline using Pydantic models.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

# Mock client implementation for example purposes
class ExtractionClientSync:
    """Mock client for example purposes."""
    
    def __init__(self, config_dir=None):
        """Initialize mock client."""
        pass
    
    def extract_text(self, text, fields, domain, output_formats=None):
        """Mock extract_text method."""
        if output_formats is None:
            output_formats = ["json", "text"]
        
        # Create mock result
        result = {
            "json_output": {
                "patient_name": "John Smith",
                "date_of_birth": "1980-05-15",
                "gender": "Male",
                "medical_record_number": "MRN-12345678",
                "allergies": ["Penicillin", "Peanuts"],
                "chronic_conditions": ["Type 2 Diabetes", "Hypertension"],
                "medications": [
                    "Metformin 500mg, twice daily",
                    "Lisinopril 10mg, once daily",
                    "Aspirin 81mg, once daily"
                ],
                "diagnoses": ["Type 2 Diabetes", "Hypertension", "Upper respiratory infection"],
                "visits": [
                    {
                        "date": "2023-03-10",
                        "provider": "Dr. Sarah Johnson",
                        "complaint": "Persistent cough and fever",
                        "assessment": "Upper respiratory infection, likely viral",
                        "plan": "Rest, increased fluids, over-the-counter cough suppressant",
                        "follow_up": "As needed if symptoms worsen"
                    },
                    {
                        "date": "2023-07-22",
                        "provider": "Dr. Michael Chen",
                        "complaint": "Routine diabetes check-up",
                        "assessment": "Type 2 Diabetes - well controlled",
                        "plan": "Continue current medications, maintain diet and exercise regimen",
                        "follow_up": "3 months"
                    },
                    {
                        "date": "2023-11-15",
                        "provider": "Dr. Sarah Johnson",
                        "complaint": "Annual physical examination",
                        "assessment": "Overall good health, mild hyperlipidemia",
                        "plan": "Dietary modifications to reduce cholesterol, continue current medications",
                        "follow_up": "Annual physical in 1 year, diabetes check-up in 3 months"
                    }
                ]
            },
            "text_output": """
Patient Name: John Smith
Date of Birth: 1980-05-15
Gender: Male
Medical Record Number: MRN-12345678
Allergies: Penicillin, Peanuts
Chronic Conditions: Type 2 Diabetes, Hypertension
Medications: Metformin 500mg (twice daily), Lisinopril 10mg (once daily), Aspirin 81mg (once daily)
Diagnoses: Type 2 Diabetes, Hypertension, Upper respiratory infection

Visits:
- 2023-03-10: Dr. Sarah Johnson - Upper respiratory infection, likely viral
- 2023-07-22: Dr. Michael Chen - Type 2 Diabetes - well controlled
- 2023-11-15: Dr. Sarah Johnson - Overall good health, mild hyperlipidemia
""",
            "metadata": {
                "processing_time": 1.25,
                "chunk_count": 3,
                "token_count": 1500
            }
        }
        
        return result


# Define Pydantic models for structured output
class MedicalVisit(BaseModel):
    """Model for a medical visit."""
    date: str = Field(description="Date of the visit")
    provider: str = Field(description="Healthcare provider name")
    complaint: Optional[str] = Field(description="Chief complaint or reason for visit")
    vital_signs: Optional[Dict[str, str]] = Field(description="Vital signs recorded during the visit")
    assessment: Optional[str] = Field(description="Provider's assessment or diagnosis")
    plan: Optional[str] = Field(description="Treatment plan")
    follow_up: Optional[str] = Field(description="Follow-up instructions")
    
    @model_validator(mode="before")
    @classmethod
    def validate_date(cls, values: dict) -> dict:
        """Validate that date is in a reasonable format."""
        if "date" in values:
            date_str = values["date"]
            try:
                # Try to parse the date
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    # Try another common format
                    datetime.strptime(date_str, "%m/%d/%Y")
                except ValueError:
                    raise ValueError(f"Date '{date_str}' is not in a valid format")
        return values


class MedicalRecord(BaseModel):
    """Model for a medical record."""
    patient_name: str = Field(description="Full name of the patient")
    date_of_birth: str = Field(description="Patient's date of birth")
    gender: Optional[str] = Field(description="Patient's gender")
    medical_record_number: Optional[str] = Field(description="Medical record number")
    allergies: Optional[List[str]] = Field(description="List of patient allergies")
    chronic_conditions: Optional[List[str]] = Field(description="List of chronic conditions")
    medications: Optional[List[str]] = Field(description="List of current medications")
    visits: Optional[List[MedicalVisit]] = Field(description="List of medical visits")


class LegalParty(BaseModel):
    """Model for a party in a legal document."""
    name: str = Field(description="Name of the party")
    type: str = Field(description="Type of entity (e.g., corporation, individual)")
    location: Optional[str] = Field(description="Location or address")
    role: str = Field(description="Role in the agreement (e.g., Client, Consultant)")


class LegalObligation(BaseModel):
    """Model for a legal obligation."""
    party: str = Field(description="Party responsible for the obligation")
    description: str = Field(description="Description of the obligation")
    deadline: Optional[str] = Field(description="Deadline for fulfilling the obligation, if applicable")


class LegalAgreement(BaseModel):
    """Model for a legal agreement."""
    title: str = Field(description="Title of the agreement")
    effective_date: str = Field(description="Date when the agreement becomes effective")
    termination_date: Optional[str] = Field(description="Date when the agreement terminates")
    parties: List[LegalParty] = Field(description="Parties involved in the agreement")
    obligations: Optional[List[LegalObligation]] = Field(description="List of obligations")
    governing_law: Optional[str] = Field(description="Governing law for the agreement")


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


def extract_with_pydantic():
    """Extract information using PydanticOutputParser."""
    print("\n=== Medical Document Extraction with PydanticOutputParser ===\n")
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    import os
    
    # Load .env file and override existing environment variables
    load_dotenv(override=True)
    
    # Get OpenAI settings from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    openai_model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    try:
        # Try to import from langchain_openai (recommended)
        from langchain_openai import ChatOpenAI
    except ImportError:
        # Fall back to langchain_community if langchain_openai is not installed
        from langchain_community.chat_models import ChatOpenAI
        print("Warning: Using deprecated ChatOpenAI from langchain_community.")
        print("Consider installing langchain_openai: pip install langchain_openai")
    
    # Initialize ChatOpenAI with settings from .env
    llm = ChatOpenAI(
        model_name=openai_model_name,
        temperature=0,
        openai_api_key=openai_api_key,
        openai_api_base=openai_base_url
    )
    
    # Set up parser
    parser = PydanticOutputParser(pydantic_object=MedicalRecord)
    
    # Create prompt template
    prompt = PromptTemplate(
        template="Extract the following information from the medical document.\n{format_instructions}\n\nDocument:\n{document}\n",
        input_variables=["document"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    # Create chain
    chain = prompt | llm | parser
    
    # Extract information
    result = chain.invoke({"document": MEDICAL_DOCUMENT})
    
    # Print results
    print("Extracted Medical Record:")
    print(f"Patient Name: {result.patient_name}")
    print(f"Date of Birth: {result.date_of_birth}")
    print(f"Gender: {result.gender}")
    print(f"Medical Record Number: {result.medical_record_number}")
    
    print("\nAllergies:")
    for allergy in result.allergies or []:
        print(f"- {allergy}")
    
    print("\nChronic Conditions:")
    for condition in result.chronic_conditions or []:
        print(f"- {condition}")
    
    print("\nMedications:")
    for medication in result.medications or []:
        print(f"- {medication}")
    
    print("\nVisits:")
    for visit in result.visits or []:
        print(f"- Date: {visit.date}")
        print(f"  Provider: {visit.provider}")
        print(f"  Complaint: {visit.complaint}")
        print(f"  Assessment: {visit.assessment}")
        print(f"  Plan: {visit.plan}")
        print(f"  Follow-up: {visit.follow_up}")
        print()
    
    # Convert to JSON for comparison with standard extraction
    result_json = result.model_dump()
    print("\nJSON Output:")
    print(json.dumps(result_json, indent=2))


def extract_with_standard_client():
    """Extract information using the standard client."""
    print("\n=== Medical Document Extraction with Standard Client ===\n")
    
    # Initialize client
    client = ExtractionClientSync(config_dir="./config")
    
    # Define fields to extract
    fields = ["patient_name", "date_of_birth", "gender", "medical_record_number", 
              "allergies", "chronic_conditions", "medications", "visits"]
    
    # Extract information
    result = client.extract_text(
        text=MEDICAL_DOCUMENT,
        fields=fields,
        domain="medical",
        output_formats=["json"]
    )
    
    # Print results
    print("JSON Output:")
    print(json.dumps(result.get("json_output", {}), indent=2))


def compare_extraction_methods():
    """Compare different extraction methods."""
    # Extract with PydanticOutputParser
    extract_with_pydantic()
    
    # Extract with standard client
    extract_with_standard_client()
    
    print("\n=== Comparison ===\n")
    print("Benefits of PydanticOutputParser:")
    print("1. Strong typing and validation through Pydantic models")
    print("2. Automatic validation of field formats (e.g., dates)")
    print("3. Clear schema definition with nested models")
    print("4. Better IDE support with type hints")
    print("5. Easy integration with FastAPI and other Pydantic-based frameworks")
    
    print("\nBenefits of Standard Extraction Pipeline:")
    print("1. More flexible for handling various document types")
    print("2. Built-in support for chunking large documents")
    print("3. Parallel processing of document chunks")
    print("4. Result merging and deduplication")
    print("5. Multiple output formats (JSON, text, XML)")
    
    print("\nRecommendation:")
    print("For production use, consider integrating PydanticOutputParser into the")
    print("extraction pipeline to get the benefits of both approaches.")


def main():
    """Main function."""
    compare_extraction_methods()


if __name__ == "__main__":
    main()
