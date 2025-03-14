"""
Example Usage of Dudoxx Extraction

This script demonstrates how to use the Dudoxx Extraction package for extracting
structured information from text documents.
"""

import json
from dudoxx_extraction.client import ExtractionClientSync

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


def extract_from_medical_document():
    """Extract information from a medical document."""
    print("\n=== Medical Document Extraction ===\n")
    
    # Initialize client
    client = ExtractionClientSync()
    
    # Define fields to extract
    fields = ["patient_name", "date_of_birth", "diagnoses", "medications", "visits"]
    
    # Extract information
    result = client.extract_text(
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


def extract_from_legal_document():
    """Extract information from a legal document."""
    print("\n=== Legal Document Extraction ===\n")
    
    # Initialize client
    client = ExtractionClientSync()
    
    # Define fields to extract
    fields = ["parties", "effective_date", "termination_date", "obligations", "events"]
    
    # Extract information
    result = client.extract_text(
        text=LEGAL_DOCUMENT,
        fields=fields,
        domain="legal",
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


def save_example_documents():
    """Save example documents to files."""
    import os
    
    # Create examples directory
    os.makedirs("examples", exist_ok=True)
    
    # Save medical document
    with open("examples/medical_record.txt", "w") as f:
        f.write(MEDICAL_DOCUMENT)
    
    # Save legal document
    with open("examples/legal_agreement.txt", "w") as f:
        f.write(LEGAL_DOCUMENT)
    
    print("Example documents saved to 'examples' directory.")


def extract_from_file():
    """Extract information from a file."""
    print("\n=== File Extraction ===\n")
    
    # Initialize client
    client = ExtractionClientSync()
    
    # Extract from medical record file
    result = client.extract_file(
        file_path="examples/medical_record.txt",
        fields=["patient_name", "date_of_birth", "diagnoses", "medications", "visits"],
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


def main():
    """Main function."""
    # Save example documents
    save_example_documents()
    
    # Extract from medical document
    extract_from_medical_document()
    
    # Extract from legal document
    extract_from_legal_document()
    
    # Extract from file
    extract_from_file()


if __name__ == "__main__":
    main()
