"""
Example Usage of the Automated Large-Text Field Extraction Solution

This script demonstrates how to use the extraction pipeline with LangChain components.
"""

import os
import asyncio
import json
from typing import List, Dict, Any

# Import rich logger
try:
    from langchain_sdk.logger import RichLogger
except ImportError:
    # When running as a script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from langchain_sdk.logger import RichLogger

# Client implementation with rich logging
class ExtractionClientSync:
    """Client for extraction with rich logging."""
    
    def __init__(self, config_dir=None, verbose=True):
        """
        Initialize client.
        
        Args:
            config_dir: Configuration directory
            verbose: Whether to log verbose output
        """
        # Initialize rich logger
        self.logger = RichLogger(verbose=verbose)
        
        # Load environment variables from .env file
        from dotenv import load_dotenv
        import os
        
        # Load .env file and override existing environment variables
        load_dotenv(override=True)
        
        # Get OpenAI settings from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL")
        self.openai_model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        self.openai_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Log environment variables
        self.logger.log_step("Environment", "Loaded environment variables", {
            "OPENAI_BASE_URL": self.openai_base_url,
            "OPENAI_MODEL_NAME": self.openai_model_name,
            "OPENAI_EMBEDDING_MODEL": self.openai_embedding_model
        })
        
        # Initialize OpenAI client
        try:
            # Try to import from langchain_openai (recommended)
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model_name=self.openai_model_name,
                temperature=0,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url
            )
            self.logger.log_step("LLM Initialization", f"Using ChatOpenAI with model {self.openai_model_name}")
        except ImportError:
            # Fall back to langchain_community if langchain_openai is not installed
            from langchain_community.chat_models import ChatOpenAI
            self.logger.log_step("LLM Initialization", f"Using deprecated ChatOpenAI from langchain_community with model {self.openai_model_name}")
            self.logger.log_step("Warning", "Consider installing langchain_openai: pip install langchain_openai")
            self.llm = ChatOpenAI(
                model_name=self.openai_model_name,
                temperature=0,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url
            )
        
        # Initialize embeddings
        try:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model=self.openai_embedding_model,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url
            )
            self.logger.log_step("Embeddings Initialization", f"Using OpenAIEmbeddings with model {self.openai_embedding_model}")
        except ImportError:
            # Fall back to langchain_community if langchain_openai is not installed
            from langchain_community.embeddings import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model=self.openai_embedding_model,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url
            )
            self.logger.log_step("Embeddings Initialization", f"Using deprecated OpenAIEmbeddings from langchain_community with model {self.openai_embedding_model}")
    
    def extract_text(self, text, fields, domain, output_formats=None):
        """
        Extract information from text using OpenAI LLM.
        
        Args:
            text: Text to extract from
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        import time
        import json
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        if output_formats is None:
            output_formats = ["json", "text"]
        
        self.logger.log_step("Processing", f"Extracting {len(fields)} fields from {domain} text")
        
        start_time = time.time()
        
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
        chain = prompt | self.llm | parser
        
        # Estimate prompt tokens
        prompt_tokens = len(prompt_template) // 4
        self.logger.log_step("LLM Request", f"Sending request with ~{prompt_tokens} tokens")
        
        # Extract information
        json_output = chain.invoke({"text": text})
        
        # Estimate completion tokens
        completion_tokens = len(json.dumps(json_output)) // 4
        self.logger.log_step("LLM Response", f"Received response with ~{completion_tokens} tokens")
        
        # Format outputs
        self.logger.log_step("Output Formatting", f"Formatting output in {output_formats}")
        
        # Format JSON output
        if "json" in output_formats:
            self.logger.log_extraction_results(json_output, "json")
        
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
        
        if "text" in output_formats:
            self.logger.log_extraction_results(text_output, "text")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create metadata
        metadata = {
            "processing_time": processing_time,
            "chunk_count": 1,
            "field_count": len(fields),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
        
        self.logger.log_metadata(metadata)
        
        # Create result
        result = {
            "json_output": json_output,
            "text_output": text_output,
            "metadata": metadata
        }
        
        return result
    
    def extract_file(self, file_path, fields, domain, output_formats=None):
        """
        Extract information from a file.
        
        Args:
            file_path: Path to the file
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        self.logger.log_step("Document Loading", f"Loading document from {file_path}")
        
        # Read file
        with open(file_path, "r") as f:
            text = f.read()
        
        # Log document loading
        self.logger.log_document_loading(file_path, 1, text.count("\n\n") + 1)
        
        # Extract from text
        return self.extract_text(text, fields, domain, output_formats)


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

4. CONFIDENTIALITY

4.1 Definition. "Confidential Information" means all non-public information disclosed by one party (the "Disclosing Party") to the other party (the "Receiving Party"), whether orally or in writing, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure.

4.2 Obligations. The Receiving Party shall: (a) protect the confidentiality of the Disclosing Party's Confidential Information using the same degree of care that it uses to protect the confidentiality of its own confidential information of like kind (but in no event less than reasonable care); (b) not use any Confidential Information of the Disclosing Party for any purpose outside the scope of this Agreement; and (c) not disclose Confidential Information to any third party without the Disclosing Party's prior written consent.

5. INTELLECTUAL PROPERTY

5.1 Client Materials. Client shall own all right, title, and interest in and to any materials provided by Client to Consultant in connection with this Agreement ("Client Materials").

5.2 Deliverables. Upon full payment of all amounts due under this Agreement, Consultant assigns to Client all right, title, and interest in and to the deliverables specified in Exhibit A ("Deliverables").

6. GENERAL PROVISIONS

6.1 Independent Contractor. Consultant is an independent contractor and not an employee of Client.

6.2 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of California without giving effect to any choice or conflict of law provision or rule.

6.3 Entire Agreement. This Agreement, including all exhibits, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior and contemporaneous agreements or communications.

IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the Effective Date.

ABC CORPORATION

By: ________________________
Name: John Executive
Title: Chief Executive Officer
Date: January 15, 2023

XYZ CONSULTING LLC

By: ________________________
Name: Jane Consultant
Title: Managing Partner
Date: January 15, 2023

EXHIBIT A
SCOPE OF SERVICES

Consultant shall provide the following Services to Client:

1. Strategic business analysis and recommendations
2. Market research and competitive analysis
3. Process optimization consulting
4. Monthly progress reports and quarterly executive briefings

EXHIBIT B
COMPENSATION

1. Consulting Fee: $10,000 per month
2. Performance Bonus: Up to $25,000 based on achievement of milestones specified in Exhibit C
3. Hourly Rate for Additional Services: $250 per hour
"""


def extract_from_medical_document():
    """Extract information from a medical document."""
    print("\n=== Medical Document Extraction ===\n")
    
    # Initialize client
    client = ExtractionClientSync(config_dir="./config")
    
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
    client = ExtractionClientSync(config_dir="./config")
    
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


def extract_from_file(file_path: str, domain: str, fields: List[str]):
    """
    Extract information from a file.
    
    Args:
        file_path: Path to the file
        domain: Domain context
        fields: Fields to extract
    """
    print(f"\n=== File Extraction ({os.path.basename(file_path)}) ===\n")
    
    # Initialize client
    client = ExtractionClientSync(config_dir="./config")
    
    # Extract information
    result = client.extract_file(
        file_path=file_path,
        fields=fields,
        domain=domain,
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
    # Create examples directory
    os.makedirs("examples", exist_ok=True)
    
    # Save medical document
    with open("examples/medical_record.txt", "w") as f:
        f.write(MEDICAL_DOCUMENT)
    
    # Save legal document
    with open("examples/legal_agreement.txt", "w") as f:
        f.write(LEGAL_DOCUMENT)
    
    print("Example documents saved to 'examples' directory.")


def main():
    """Main function."""
    # Save example documents
    save_example_documents()
    
    # Extract from medical document
    extract_from_medical_document()
    
    # Extract from legal document
    extract_from_legal_document()
    
    # Extract from file
    extract_from_file(
        file_path="examples/medical_record.txt",
        domain="medical",
        fields=["patient_name", "date_of_birth", "diagnoses", "medications", "visits"]
    )


if __name__ == "__main__":
    main()
