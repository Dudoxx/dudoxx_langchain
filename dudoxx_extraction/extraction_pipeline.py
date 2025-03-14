"""
Dudoxx Extraction - Automated Large-Text Field Extraction Solution

This module implements the extraction pipeline using LangChain components.
"""

import asyncio
import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Union, Type

# LangChain imports
from langchain_community.document_loaders import TextLoader, PyPDFLoader, AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
try:
    from langchain_core.chains import LLMChain
except ImportError:
    from langchain.chains import LLMChain
import numpy as np

# Try to import from langchain_openai (recommended)
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fall back to langchain_community if langchain_openai is not installed
    from langchain_community.chat_models import ChatOpenAI
    print("Warning: Using deprecated ChatOpenAI from langchain_community.")
    print("Consider installing langchain_openai: pip install langchain_openai")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    import os
    
    # Load .env file and override existing environment variables
    load_dotenv(override=True)
    
    # Get OpenAI settings from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
except ImportError:
    # python-dotenv not installed
    import os
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")


class TemporalNormalizer:
    """Normalizes dates and constructs timelines."""
    
    def __init__(self, llm=None):
        """
        Initialize with LLM for complex date parsing.
        
        Args:
            llm: LangChain LLM for complex date parsing
        """
        if llm is None:
            # Initialize ChatOpenAI with settings from .env
            self.llm = ChatOpenAI(
                model_name=OPENAI_MODEL_NAME,
                temperature=0,
                openai_api_key=OPENAI_API_KEY,
                openai_api_base=OPENAI_BASE_URL
            )
        else:
            self.llm = llm
            
        self.date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y"
        ]
    
    def normalize_date(self, date_string: str) -> Optional[str]:
        """
        Normalize date to YYYY-MM-DD format.
        
        Args:
            date_string: Date string to normalize
            
        Returns:
            Normalized date string or None if parsing fails
        """
        if not date_string or not isinstance(date_string, str):
            return None
            
        # Try pattern matching first
        for date_format in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If pattern matching fails, use LLM for complex cases
        prompt = PromptTemplate(
            template="Convert the following date to YYYY-MM-DD format: {date}",
            input_variables=["date"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(date=date_string)
        
        # Extract date using regex
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', result)
        if date_match:
            return date_match.group(0)
        
        return None
    
    def construct_timeline(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Construct timeline by normalizing dates and sorting events.
        
        Args:
            events: List of events with date fields
            
        Returns:
            Sorted timeline with normalized dates
        """
        if not events:
            return []
            
        # Normalize dates
        for event in events:
            if "date" in event:
                normalized_date = self.normalize_date(event["date"])
                if normalized_date:
                    event["normalized_date"] = normalized_date
        
        # Sort events by normalized date
        sorted_events = sorted(
            events, 
            key=lambda x: x.get("normalized_date", x.get("date", ""))
        )
        
        return sorted_events


class ResultMerger:
    """Merges and deduplicates results from multiple chunks."""
    
    def __init__(self, embedding_model=None, deduplication_threshold=0.9):
        """
        Initialize with embedding model for deduplication.
        
        Args:
            embedding_model: LangChain embedding model
            deduplication_threshold: Similarity threshold for deduplication
        """
        # Use the embedding model from environment variables
        if embedding_model is None:
            try:
                # Try to import from langchain_openai (recommended)
                from langchain_openai import OpenAIEmbeddings
                self.embedding_model = OpenAIEmbeddings(
                    model=OPENAI_EMBEDDING_MODEL,
                    openai_api_key=OPENAI_API_KEY,
                    openai_api_base=OPENAI_BASE_URL
                )
            except ImportError:
                # Fall back to langchain_community if langchain_openai is not installed
                self.embedding_model = OpenAIEmbeddings(
                    model=OPENAI_EMBEDDING_MODEL,
                    openai_api_key=OPENAI_API_KEY,
                    openai_api_base=OPENAI_BASE_URL
                )
        else:
            self.embedding_model = embedding_model
        self.deduplication_threshold = deduplication_threshold
    
    def merge_results(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge results from multiple chunks.
        
        Args:
            chunk_results: List of results from chunks
            
        Returns:
            Merged and deduplicated result
        """
        merged_fields = {}
        field_sources = {}
        field_confidences = {}
        
        # Collect all field values
        for i, result in enumerate(chunk_results):
            for field_name, value in result.items():
                if field_name not in merged_fields:
                    merged_fields[field_name] = []
                    field_sources[field_name] = []
                    field_confidences[field_name] = []
                
                merged_fields[field_name].append(value)
                field_sources[field_name].append(i)
                # Assuming confidence is 1.0 if not provided
                field_confidences[field_name].append(1.0)
        
        # Deduplicate and merge
        final_result = {}
        for field_name, values in merged_fields.items():
            if len(values) == 1:
                # Only one value, no need to deduplicate
                final_result[field_name] = values[0]
            else:
                # Multiple values, need to deduplicate
                if isinstance(values[0], list):
                    # Field is a list, merge all items and deduplicate
                    all_items = []
                    for value in values:
                        if value is not None:
                            all_items.extend(value)
                    final_result[field_name] = self._deduplicate_list(all_items)
                else:
                    # Field is a single value, choose the most confident one
                    best_index = np.argmax(field_confidences[field_name])
                    final_result[field_name] = values[best_index]
        
        # Add metadata
        final_result["_metadata"] = {
            "source_chunks": field_sources,
            "confidence": field_confidences
        }
        
        return final_result
    
    def _deduplicate_list(self, items: List[Any]) -> List[Any]:
        """
        Deduplicate a list of items using embeddings.
        
        Args:
            items: List of items to deduplicate
            
        Returns:
            Deduplicated list
        """
        if not items:
            return []
        
        if all(isinstance(item, str) for item in items):
            # Text items, use embeddings for deduplication
            unique_items = []
            
            # Create vector store with first item
            vector_store = FAISS.from_texts([items[0]], self.embedding_model)
            unique_items.append(items[0])
            
            # Check each item against vector store
            for item in items[1:]:
                results = vector_store.similarity_search_with_score(item, k=1)
                
                if not results or results[0][1] > self.deduplication_threshold:
                    # Item is unique, add to vector store and unique items
                    vector_store.add_texts([item])
                    unique_items.append(item)
            
            return unique_items
        else:
            # Non-text items, use equality for deduplication
            return list(set(items))


class OutputFormatter:
    """Formats extraction results in different formats."""
    
    def format_json(self, merged_result: Dict[str, Any], include_metadata: bool = True) -> Dict[str, Any]:
        """
        Format result as JSON.
        
        Args:
            merged_result: Merged extraction result
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted JSON result
        """
        result = merged_result.copy()
        
        if not include_metadata:
            # Remove metadata fields
            keys_to_remove = [key for key in result if key.startswith("_")]
            for key in keys_to_remove:
                del result[key]
        
        return result
    
    def format_text(self, merged_result: Dict[str, Any]) -> str:
        """
        Format result as flat text for embeddings.
        
        Args:
            merged_result: Merged extraction result
            
        Returns:
            Formatted text result
        """
        lines = []
        
        # Add regular fields
        for field_name, value in merged_result.items():
            if field_name.startswith("_"):
                # Skip metadata fields
                continue
                
            if isinstance(value, list):
                # Format list values
                for item in value:
                    if isinstance(item, dict):
                        # Format dictionary items
                        item_str = ", ".join([f"{k}: {v}" for k, v in item.items()])
                        lines.append(f"{field_name}: {item_str}")
                    else:
                        # Format simple items
                        lines.append(f"{field_name}: {item}")
            elif isinstance(value, dict):
                # Format dictionary values
                for k, v in value.items():
                    lines.append(f"{field_name}.{k}: {v}")
            else:
                # Format single value
                lines.append(f"{field_name}: {value}")
        
        # Add timeline if present
        if "timeline" in merged_result:
            lines.append("")  # Empty line before timeline
            lines.append("Timeline:")
            
            for event in merged_result["timeline"]:
                date = event.get("date", "")
                description = event.get("description", "")
                lines.append(f"{date}: {description}")
        
        return "\n".join(lines)
    
    def format_xml(self, merged_result: Dict[str, Any]) -> str:
        """
        Format result as XML.
        
        Args:
            merged_result: Merged extraction result
            
        Returns:
            Formatted XML result
        """
        import xml.dom.minidom as md
        import xml.etree.ElementTree as ET
        
        # Create root element
        root = ET.Element("Document")
        
        # Add fields
        fields_elem = ET.SubElement(root, "Fields")
        for field_name, value in merged_result.items():
            if field_name.startswith("_"):
                # Skip metadata fields
                continue
                
            self._add_xml_element(fields_elem, field_name, value)
        
        # Add metadata if present
        if "_metadata" in merged_result:
            metadata_elem = ET.SubElement(root, "Metadata")
            for key, value in merged_result["_metadata"].items():
                self._add_xml_element(metadata_elem, key, value)
        
        # Convert to string and pretty print
        xml_str = ET.tostring(root, encoding="unicode")
        pretty_xml = md.parseString(xml_str).toprettyxml(indent="  ")
        
        return pretty_xml
    
    def _add_xml_element(self, parent: Any, name: str, value: Any) -> None:
        """
        Add element to XML parent.
        
        Args:
            parent: Parent XML element
            name: Element name
            value: Element value
        """
        import xml.etree.ElementTree as ET
        
        if value is None:
            ET.SubElement(parent, name, null="true")
        elif isinstance(value, list):
            list_elem = ET.SubElement(parent, name)
            
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    item_elem = ET.SubElement(list_elem, "Item", index=str(i))
                    for k, v in item.items():
                        self._add_xml_element(item_elem, k, v)
                else:
                    ET.SubElement(list_elem, "Item").text = str(item)
        elif isinstance(value, dict):
            dict_elem = ET.SubElement(parent, name)
            for k, v in value.items():
                self._add_xml_element(dict_elem, k, v)
        else:
            ET.SubElement(parent, name).text = str(value)


class ExtractionPipeline:
    """Main pipeline for document extraction."""
    
    def __init__(self, 
                 document_loader: Union[Type[TextLoader], Type[PyPDFLoader], Type[AzureAIDocumentIntelligenceLoader]] = None,
                 text_splitter: RecursiveCharacterTextSplitter = None,
                 llm = None,
                 output_parser: PydanticOutputParser = None,
                 temporal_normalizer: TemporalNormalizer = None,
                 result_merger: ResultMerger = None,
                 output_formatter: OutputFormatter = None,
                 max_concurrency: int = 20):
        """
        Initialize extraction pipeline.
        
        Args:
            document_loader: LangChain document loader class
            text_splitter: LangChain text splitter
            llm: LangChain LLM
            output_parser: LangChain output parser
            temporal_normalizer: Temporal normalizer
            result_merger: Result merger
            output_formatter: Output formatter
            max_concurrency: Maximum concurrent LLM requests
        """
        self.document_loader = document_loader or TextLoader
        
        self.text_splitter = text_splitter or RecursiveCharacterTextSplitter(
            chunk_size=16000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize ChatOpenAI with settings from .env
        self.llm = llm or ChatOpenAI(
            model_name=OPENAI_MODEL_NAME,
            temperature=0,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL
        )
        
        self.output_parser = output_parser
        self.temporal_normalizer = temporal_normalizer or TemporalNormalizer(self.llm)
        self.result_merger = result_merger or ResultMerger()
        self.output_formatter = output_formatter or OutputFormatter()
        self.max_concurrency = max_concurrency
    
    async def process_document(self, 
                              document_path: str, 
                              fields: List[str], 
                              domain: str, 
                              output_formats: List[str] = ["json", "text"]) -> Dict[str, Any]:
        """
        Process a document through the extraction pipeline.
        
        Args:
            document_path: Path to document
            fields: Fields to extract
            domain: Domain context
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        start_time = time.time()
        
        # Step 1: Load document
        loader = self.document_loader(document_path)
        documents = loader.load()
        
        # Step 2: Split document into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Step 3: Process chunks in parallel
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def process_chunk(chunk):
            async with semaphore:
                # Generate prompt
                prompt = self._generate_prompt(chunk.page_content, fields, domain)
                
                # Process with LLM
                response = await self.llm.agenerate([prompt])
                
                # Parse output
                try:
                    parsed_output = self.output_parser.parse(response.generations[0][0].text)
                    return parsed_output
                except Exception as e:
                    print(f"Error parsing output: {e}")
                    print(f"Raw output: {response.generations[0][0].text}")
                    # Return empty result on parsing error
                    return {field: None for field in fields}
        
        # Create tasks for all chunks
        tasks = [process_chunk(chunk) for chunk in chunks]
        
        # Execute tasks in parallel
        chunk_results = await asyncio.gather(*tasks)
        
        # Step 4: Normalize temporal data
        normalized_results = []
        for result in chunk_results:
            normalized_result = {}
            for field, value in result.items():
                if field.endswith("_date") or field == "date":
                    # Normalize date fields
                    normalized_result[field] = self.temporal_normalizer.normalize_date(value)
                elif field == "timeline" and isinstance(value, list):
                    # Normalize timeline
                    normalized_result[field] = self.temporal_normalizer.construct_timeline(value)
                else:
                    normalized_result[field] = value
            
            normalized_results.append(normalized_result)
        
        # Step 5: Merge and deduplicate results
        merged_result = self.result_merger.merge_results(normalized_results)
        
        # Step 6: Format output
        output = {}
        if "json" in output_formats:
            output["json_output"] = self.output_formatter.format_json(merged_result)
        
        if "text" in output_formats:
            output["text_output"] = self.output_formatter.format_text(merged_result)
            
        if "xml" in output_formats:
            output["xml_output"] = self.output_formatter.format_xml(merged_result)
        
        # Add metadata
        processing_time = time.time() - start_time
        output["metadata"] = {
            "processing_time": processing_time,
            "chunk_count": len(chunks),
            "field_count": len(fields),
            "token_count": self._estimate_token_count(chunks)
        }
        
        return output
    
    def _generate_prompt(self, text: str, fields: List[str], domain: str) -> str:
        """
        Generate prompt for field extraction.
        
        Args:
            text: Text to extract from
            fields: Fields to extract
            domain: Domain context
            
        Returns:
            Prompt for LLM
        """
        field_descriptions = {
            "patient_name": "Full name of the patient",
            "date_of_birth": "Patient's date of birth",
            "diagnoses": "List of diagnoses",
            "medications": "List of medications",
            "visits": "List of medical visits with dates and descriptions",
            "parties": "Parties involved in the contract",
            "effective_date": "Date when the contract becomes effective",
            "termination_date": "Date when the contract terminates",
            "obligations": "List of obligations for each party",
            "events": "List of events with dates and descriptions"
            # Add more field descriptions as needed
        }
        
        # Create field list for prompt
        field_list = "\n".join([f"- {field}: {field_descriptions.get(field, '')}" for field in fields])
        
        # Create prompt
        prompt = f"""Extract the following information from the {domain} document:

{field_list}

Return the information in JSON format with the field names as keys.
If a field is not found in the text, return null for that field.
If a field can have multiple values, return them as a list.

Text:
{text}
"""
        return prompt
    
    def _estimate_token_count(self, chunks: List[Any]) -> int:
        """
        Estimate token count for chunks.
        
        Args:
            chunks: Document chunks
            
        Returns:
            Estimated token count
        """
        # Simple estimation: 1 token ≈ 4 characters
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        return total_chars // 4


# Synchronous wrapper for the extraction pipeline
def extract_text(
    text: str,
    fields: List[str],
    domain: str,
    output_formats: List[str] = ["json", "text"]
) -> Dict[str, Any]:
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
    import time
    import json
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    
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


def extract_file(
    file_path: str,
    fields: List[str],
    domain: str,
    output_formats: List[str] = ["json", "text"]
) -> Dict[str, Any]:
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
