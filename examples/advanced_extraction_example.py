"""
Advanced Extraction Example using LangChain 0.3 Features

This script demonstrates how to use advanced LangChain 0.3 features for document extraction,
including structured output extraction, semantic search, and ReAct pattern.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from rich.console import Console
from rich.panel import Panel

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import LangChain components
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pydantic import BaseModel, Field

# Import Dudoxx components
from dudoxx_extraction.configuration_service import ConfigurationService
from dudoxx_extraction.document_loaders import DocumentLoaderFactory

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

# Define output schemas using Pydantic models
class Medication(BaseModel):
    """Schema for a medication."""
    name: str = Field(description="Name of the medication")
    dosage: str = Field(description="Dosage of the medication")
    frequency: str = Field(description="Frequency of the medication")
    purpose: Optional[str] = Field(description="Purpose of the medication", default=None)

class Visit(BaseModel):
    """Schema for a medical visit."""
    date: str = Field(description="Date of the visit")
    provider: str = Field(description="Provider who conducted the visit")
    complaint: str = Field(description="Chief complaint or reason for the visit")
    vital_signs: Optional[Dict[str, str]] = Field(description="Vital signs recorded during the visit", default=None)
    assessment: str = Field(description="Assessment or diagnosis from the visit")
    plan: str = Field(description="Treatment plan from the visit")
    follow_up: Optional[str] = Field(description="Follow-up instructions from the visit", default=None)

class MedicalRecord(BaseModel):
    """Schema for a medical record."""
    patient_name: str = Field(description="Patient's full name")
    date_of_birth: str = Field(description="Patient's date of birth")
    gender: Optional[str] = Field(description="Patient's gender", default=None)
    medical_record_number: Optional[str] = Field(description="Patient's medical record number", default=None)
    allergies: List[str] = Field(description="List of patient's allergies")
    chronic_conditions: List[Dict[str, str]] = Field(description="List of patient's chronic conditions with diagnosis dates")
    medications: List[Medication] = Field(description="List of patient's current medications")
    visits: List[Visit] = Field(description="List of patient's visits")


class AdvancedExtractionExample:
    """Advanced extraction example using LangChain 0.3 features."""

    def __init__(self):
        """Initialize the example."""
        self.console = Console()
        self.config_service = ConfigurationService()
        
        # Get LLM and embedding configurations
        self.llm_config = self.config_service.get_llm_config()
        self.embedding_config = self.config_service.get_embedding_config()
        
        # Create LLM and embeddings
        self.llm = ChatOpenAI(
            base_url=self.llm_config["base_url"],
            api_key=self.llm_config["api_key"],
            model_name=self.llm_config["model_name"],
            temperature=self.llm_config["temperature"]
        )
        
        self.embeddings = OpenAIEmbeddings(
            base_url=self.embedding_config["base_url"],
            api_key=self.embedding_config["api_key"],
            model=self.embedding_config["model"]
        )
        
        # Create text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def extract_with_structured_output(self, text: str) -> MedicalRecord:
        """
        Extract information using structured output.
        
        This method uses the with_structured_output feature of LangChain 0.3
        to extract structured information from text.
        
        Args:
            text: The text to extract information from.
            
        Returns:
            MedicalRecord: The extracted information.
        """
        self.console.print(Panel("Extracting with Structured Output", style="cyan"))
        
        # Create a model with structured output capability
        structured_llm = self.llm.with_structured_output(MedicalRecord)
        
        # Extract information
        result = structured_llm.invoke(text)
        
        return result

    def extract_with_semantic_search(self, text: str) -> MedicalRecord:
        """
        Extract information using semantic search.
        
        This method uses semantic search to find relevant information in the text
        before extracting structured information.
        
        Args:
            text: The text to extract information from.
            
        Returns:
            MedicalRecord: The extracted information.
        """
        self.console.print(Panel("Extracting with Semantic Search", style="cyan"))
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create vector store
        vectorstore = FAISS.from_texts(chunks, self.embeddings)
        
        # Create retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Create extraction chain
        extraction_chain = (
            {"query": RunnablePassthrough(), "docs": retriever}
            | self._process_retrieved_docs
            | self.llm.with_structured_output(MedicalRecord)
        )
        
        # Extract information
        queries = [
            "Extract patient information",
            "Extract medical history",
            "Extract medications",
            "Extract visit history"
        ]
        
        # Run extraction for each query and merge results
        results = []
        for query in queries:
            self.console.print(f"Running query: {query}")
            result = extraction_chain.invoke(query)
            results.append(result)
        
        # Merge results (in a real implementation, you would need a more sophisticated merging strategy)
        merged_result = results[0]
        
        return merged_result

    def _process_retrieved_docs(self, inputs: Dict[str, Any]) -> str:
        """Process retrieved documents."""
        query = inputs["query"]
        docs = inputs["docs"]
        
        # Combine document content
        doc_content = "\n\n".join([doc.page_content for doc in docs])
        
        return f"Query: {query}\n\nRelevant Information:\n{doc_content}"

    def extract_with_react_pattern(self, text: str) -> MedicalRecord:
        """
        Extract information using the ReAct pattern.
        
        This method uses the ReAct pattern (Reasoning + Acting) to extract
        structured information from text.
        
        Args:
            text: The text to extract information from.
            
        Returns:
            MedicalRecord: The extracted information.
        """
        self.console.print(Panel("Extracting with ReAct Pattern", style="cyan"))
        
        # Step 1: Reasoning - Analyze the document structure
        reasoning_prompt = ChatPromptTemplate.from_template(
            "You are analyzing a medical document to extract structured information.\n\n"
            "Document:\n{text}\n\n"
            "Think step by step about how to extract the following information:\n"
            "1. Patient name and date of birth\n"
            "2. Allergies and chronic conditions\n"
            "3. Current medications\n"
            "4. Visit history\n\n"
            "Provide a detailed plan for extraction."
        )
        
        reasoning_chain = reasoning_prompt | self.llm | StrOutputParser()
        reasoning_result = reasoning_chain.invoke({"text": text})
        
        self.console.print("Reasoning:")
        self.console.print(reasoning_result)
        
        # Step 2: Acting - Extract the information based on the reasoning
        extraction_prompt = ChatPromptTemplate.from_template(
            "You are extracting structured information from a medical document.\n\n"
            "Document:\n{text}\n\n"
            "Based on this reasoning plan:\n{reasoning}\n\n"
            "Extract the information and format it according to the specified structure."
        )
        
        extraction_chain = (
            extraction_prompt 
            | self.llm.with_structured_output(MedicalRecord)
        )
        
        extraction_result = extraction_chain.invoke({
            "text": text,
            "reasoning": reasoning_result
        })
        
        return extraction_result

    def extract_from_file(self, file_path: str) -> MedicalRecord:
        """
        Extract information from a file.
        
        This method loads a document from a file and extracts structured information.
        
        Args:
            file_path: Path to the file to extract information from.
            
        Returns:
            MedicalRecord: The extracted information.
        """
        self.console.print(Panel(f"Extracting from File: {file_path}", style="cyan"))
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.console.print(f"File not found: {file_path}", style="red")
            return None
        
        # Get loader for file
        if not DocumentLoaderFactory.is_supported_file(file_path):
            self.console.print(f"Unsupported file type: {file_path}", style="red")
            return None
        
        # Load document
        loader = DocumentLoaderFactory.get_loader_for_file(file_path)
        documents = loader.load()
        
        # Extract text from documents
        text = "\n\n".join([doc.page_content for doc in documents])
        
        # Extract information using structured output
        return self.extract_with_structured_output(text)

    def run_examples(self):
        """Run all extraction examples."""
        # Save example document to file
        example_dir = Path("examples")
        example_dir.mkdir(exist_ok=True)
        
        example_file = example_dir / "medical_record.txt"
        with open(example_file, "w") as f:
            f.write(MEDICAL_DOCUMENT)
        
        self.console.print(f"Saved example document to {example_file}")
        
        # Extract with structured output
        structured_result = self.extract_with_structured_output(MEDICAL_DOCUMENT)
        self.console.print("\nStructured Output Result:")
        self.console.print(structured_result.json(indent=2))
        
        # Extract with semantic search
        semantic_result = self.extract_with_semantic_search(MEDICAL_DOCUMENT)
        self.console.print("\nSemantic Search Result:")
        self.console.print(semantic_result.json(indent=2))
        
        # Extract with ReAct pattern
        react_result = self.extract_with_react_pattern(MEDICAL_DOCUMENT)
        self.console.print("\nReAct Pattern Result:")
        self.console.print(react_result.json(indent=2))
        
        # Extract from file
        file_result = self.extract_from_file(str(example_file))
        self.console.print("\nFile Extraction Result:")
        self.console.print(file_result.json(indent=2))
        
        # Compare results
        self.console.print("\nComparison of Extraction Methods:")
        self.console.print(f"Structured Output: {len(structured_result.visits)} visits extracted")
        self.console.print(f"Semantic Search: {len(semantic_result.visits)} visits extracted")
        self.console.print(f"ReAct Pattern: {len(react_result.visits)} visits extracted")
        self.console.print(f"File Extraction: {len(file_result.visits)} visits extracted")


def main():
    """Main function."""
    example = AdvancedExtractionExample()
    example.run_examples()


if __name__ == "__main__":
    main()
