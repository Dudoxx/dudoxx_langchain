"""
Automated Large-Text Field Extraction Solution using LangChain

This module implements the extraction pipeline using LangChain components.
"""

import asyncio
import time
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Union, Type

# Import rich logger
try:
    from langchain_sdk.logger import RichLogger
except ImportError:
    # When running as a script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from langchain_sdk.logger import RichLogger

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


class TemporalNormalizer:
    """Normalizes dates and constructs timelines."""
    
    def __init__(self, llm, logger: Optional[RichLogger] = None):
        """
        Initialize with LLM for complex date parsing.
        
        Args:
            llm: LangChain LLM for complex date parsing
            logger: Rich logger
        """
        self.llm = llm
        self.logger = logger
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
        if self.logger:
            self.logger.log_step("Date Normalization", f"Using LLM to normalize date: {date_string}")
            
        prompt = PromptTemplate(
            template="Convert the following date to YYYY-MM-DD format: {date}",
            input_variables=["date"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(date=date_string)
        
        # Extract date using regex
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', result)
        if date_match:
            normalized_date = date_match.group(0)
            if self.logger:
                self.logger.log_step("Date Normalization", f"Normalized date: {date_string} -> {normalized_date}")
            return normalized_date
        
        if self.logger:
            self.logger.log_step("Date Normalization", f"Failed to normalize date: {date_string}")
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
            
        if self.logger:
            self.logger.log_step("Timeline Construction", f"Constructing timeline with {len(events)} events")
            
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
        
        if self.logger:
            self.logger.log_step("Timeline Construction", f"Timeline constructed with {len(sorted_events)} events")
            
        return sorted_events


class ResultMerger:
    """Merges and deduplicates results from multiple chunks."""
    
    def __init__(self, embedding_model=None, deduplication_threshold=0.9, logger: Optional[RichLogger] = None):
        """
        Initialize with embedding model for deduplication.
        
        Args:
            embedding_model: LangChain embedding model
            deduplication_threshold: Similarity threshold for deduplication
            logger: Rich logger
        """
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.deduplication_threshold = deduplication_threshold
        self.logger = logger
    
    def merge_results(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge results from multiple chunks.
        
        Args:
            chunk_results: List of results from chunks
            
        Returns:
            Merged and deduplicated result
        """
        if self.logger:
            self.logger.log_step("Result Merging", f"Merging results from {len(chunk_results)} chunks")
            
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
        
        if self.logger:
            self.logger.log_step("Result Merging", f"Merged {len(merged_fields)} fields")
            
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
        
        if self.logger:
            self.logger.log_step("Deduplication", f"Deduplicating {len(items)} items")
            
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
            
            if self.logger:
                self.logger.log_step("Deduplication", f"Deduplicated {len(items)} items to {len(unique_items)} unique items")
                
            return unique_items
        else:
            # Non-text items, use equality for deduplication
            unique_items = list(set(items))
            
            if self.logger:
                self.logger.log_step("Deduplication", f"Deduplicated {len(items)} items to {len(unique_items)} unique items")
                
            return unique_items


class OutputFormatter:
    """Formats extraction results in different formats."""
    
    def __init__(self, logger: Optional[RichLogger] = None):
        """
        Initialize output formatter.
        
        Args:
            logger: Rich logger
        """
        self.logger = logger
    
    def format_json(self, merged_result: Dict[str, Any], include_metadata: bool = True) -> Dict[str, Any]:
        """
        Format result as JSON.
        
        Args:
            merged_result: Merged extraction result
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted JSON result
        """
        if self.logger:
            self.logger.log_step("Output Formatting", "Formatting output as JSON")
            
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
        if self.logger:
            self.logger.log_step("Output Formatting", "Formatting output as text")
            
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
        if self.logger:
            self.logger.log_step("Output Formatting", "Formatting output as XML")
            
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
                 document_loader: Union[Type[TextLoader], Type[PyPDFLoader], Type[AzureAIDocumentIntelligenceLoader]],
                 text_splitter: RecursiveCharacterTextSplitter,
                 llm: OpenAI,
                 output_parser: PydanticOutputParser,
                 temporal_normalizer: Optional[TemporalNormalizer] = None,
                 result_merger: Optional[ResultMerger] = None,
                 output_formatter: Optional[OutputFormatter] = None,
                 max_concurrency: int = 20,
                 logger: Optional[RichLogger] = None):
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
            logger: Rich logger
        """
        self.document_loader = document_loader
        self.text_splitter = text_splitter
        self.llm = llm
        self.output_parser = output_parser
        self.logger = logger
        
        # Initialize components with logger
        self.temporal_normalizer = temporal_normalizer or TemporalNormalizer(llm, logger)
        self.result_merger = result_merger or ResultMerger(logger=logger)
        self.output_formatter = output_formatter or OutputFormatter(logger)
        
        self.max_concurrency = max_concurrency
        
        # Log pipeline initialization
        if self.logger:
            # Get LLM and embedder information
            llm_name = getattr(llm, "__class__", "Unknown").__name__
            llm_model = getattr(llm, "model_name", "Unknown")
            
            # Get embedder information
            embedder = getattr(self.result_merger, "embedding_model", None)
            embedder_name = getattr(embedder, "__class__", "Unknown").__name__
            embedder_model = getattr(embedder, "model", "Unknown")
            
            # Get text splitter information
            chunk_size = getattr(text_splitter, "_chunk_size", "Unknown")
            chunk_overlap = getattr(text_splitter, "_chunk_overlap", "Unknown")
            
            # Log pipeline configuration
            self.logger.start_pipeline({
                "llm_name": llm_name,
                "llm_model": llm_model,
                "embedder_name": embedder_name,
                "embedder_model": embedder_model,
                "max_concurrency": max_concurrency,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            })
    
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
        if self.logger:
            self.logger.log_step("Document Loading", f"Loading document from {document_path}")
            
        loader = self.document_loader(document_path)
        documents = loader.load()
        
        if self.logger:
            page_count = sum(1 for doc in documents for _ in doc.page_content.split("\n\n"))
            self.logger.log_document_loading(document_path, len(documents), page_count)
        
        # Step 2: Split document into chunks
        if self.logger:
            self.logger.log_step("Document Chunking", "Splitting document into chunks")
            
        chunks = self.text_splitter.split_documents(documents)
        
        if self.logger:
            self.logger.log_chunking(
                len(chunks), 
                getattr(self.text_splitter, "_chunk_size", 16000), 
                getattr(self.text_splitter, "_chunk_overlap", 200)
            )
        
        # Step 3: Process chunks in parallel
        if self.logger:
            self.logger.log_step("Chunk Processing", f"Processing {len(chunks)} chunks with concurrency {self.max_concurrency}")
            
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def process_chunk(chunk_index, chunk):
            async with semaphore:
                # Generate prompt
                prompt = self._generate_prompt(chunk.page_content, fields, domain)
                
                # Estimate prompt tokens
                prompt_tokens = len(prompt) // 4
                
                if self.logger:
                    self.logger.log_llm_request(chunk_index, len(chunk.page_content), prompt_tokens)
                
                # Process with LLM
                try:
                    response = await self.llm.agenerate([prompt])
                    
                    # Estimate completion tokens
                    completion_text = response.generations[0][0].text
                    completion_tokens = len(completion_text) // 4
                    
                    # Parse output
                    try:
                        parsed_output = self.output_parser.parse(completion_text)
                        
                        if self.logger:
                            self.logger.log_llm_response(chunk_index, completion_tokens, True)
                            
                        return parsed_output
                    except Exception as e:
                        error_message = f"Error parsing output: {e}"
                        
                        if self.logger:
                            self.logger.log_llm_response(chunk_index, completion_tokens, False, error_message)
                            self.logger.log_error(error_message, completion_text)
                            
                        # Return empty result on parsing error
                        return {field: None for field in fields}
                except Exception as e:
                    error_message = f"Error generating response: {e}"
                    
                    if self.logger:
                        self.logger.log_llm_response(chunk_index, 0, False, error_message)
                        self.logger.log_error(error_message)
                        
                    # Return empty result on generation error
                    return {field: None for field in fields}
        
        # Create tasks for all chunks
        tasks = [process_chunk(i, chunk) for i, chunk in enumerate(chunks)]
        
        # Execute tasks in parallel
        chunk_results = await asyncio.gather(*tasks)
        
        # Step 4: Normalize temporal data
        if self.logger:
            self.logger.log_step("Temporal Normalization", "Normalizing temporal data")
            
        normalized_results = []
        for result in chunk_results:
            normalized_result = {}
            
            # Convert Pydantic model to dict if needed
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            else:
                result_dict = result
                
            for field, value in result_dict.items():
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
        if self.logger:
            self.logger.log_step("Result Merging", "Merging and deduplicating results")
            
        merged_result = self.result_merger.merge_results(normalized_results)
        
        # Step 6: Format output
        if self.logger:
            self.logger.log_step("Output Formatting", f"Formatting output in {output_formats}")
            
        output = {}
        if "json" in output_formats:
            output["json_output"] = self.output_formatter.format_json(merged_result)
            
            if self.logger:
                self.logger.log_extraction_results(output["json_output"], "json")
        
        if "text" in output_formats:
            output["text_output"] = self.output_formatter.format_text(merged_result)
            
            if self.logger:
                self.logger.log_extraction_results(output["text_output"], "text")
            
        if "xml" in output_formats:
            output["xml_output"] = self.output_formatter.format_xml(merged_result)
            
            if self.logger:
                self.logger.log_extraction_results(output["xml_output"], "xml")
        
        # Add metadata
        processing_time = time.time() - start_time
        
        # Calculate token usage
        prompt_tokens = sum(len(chunk.page_content) // 4 for chunk in chunks)
        
        # Convert Pydantic models to dictionaries for JSON serialization
        serializable_results = []
        for result in chunk_results:
            if hasattr(result, "model_dump"):
                serializable_results.append(result.model_dump())
            elif hasattr(result, "dict"):
                serializable_results.append(result.dict())
            else:
                serializable_results.append(result)
                
        completion_tokens = sum(len(json.dumps(result)) // 4 for result in serializable_results)
        total_tokens = prompt_tokens + completion_tokens
        
        metadata = {
            "processing_time": processing_time,
            "chunk_count": len(chunks),
            "field_count": len(fields),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
        
        output["metadata"] = metadata
        
        if self.logger:
            self.logger.log_metadata(metadata)
            
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


async def main():
    """Example usage of the extraction pipeline."""
    # Initialize rich logger
    logger = RichLogger(verbose=True)
    
    # Initialize components
    document_loader = PyPDFLoader
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=16000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
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
        OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    except ImportError:
        # python-dotenv not installed
        import os
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
        OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
        OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    logger.log_step("Environment", "Loaded environment variables", {
        "OPENAI_BASE_URL": OPENAI_BASE_URL,
        "OPENAI_MODEL_NAME": OPENAI_MODEL_NAME,
        "OPENAI_EMBEDDING_MODEL": OPENAI_EMBEDDING_MODEL
    })
    
    # Use ChatOpenAI instead of OpenAI
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model_name=OPENAI_MODEL_NAME,
            temperature=0,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL
        )
        logger.log_step("LLM Initialization", f"Using ChatOpenAI with model {OPENAI_MODEL_NAME}")
    except ImportError:
        # Fall back to langchain_community if langchain_openai is not installed
        from langchain_community.chat_models import ChatOpenAI
        logger.log_step("LLM Initialization", f"Using deprecated ChatOpenAI from langchain_community with model {OPENAI_MODEL_NAME}")
        logger.log_step("Warning", "Consider installing langchain_openai: pip install langchain_openai")
        llm = ChatOpenAI(
            model_name=OPENAI_MODEL_NAME,
            temperature=0,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL
        )
    
    # Define fields to extract
    fields = ["patient_name", "date_of_birth", "diagnoses", "medications", "visits"]
    
    # Create Pydantic model for extraction
    class ExtractionModel(BaseModel):
        patient_name: Optional[str] = Field(description="Full name of the patient")
        date_of_birth: Optional[str] = Field(description="Patient's date of birth")
        diagnoses: Optional[List[str]] = Field(description="List of diagnoses")
        medications: Optional[List[str]] = Field(description="List of medications")
        visits: Optional[List[Dict[str, Any]]] = Field(description="List of medical visits with dates and descriptions")
    
    # Create output parser
    output_parser = PydanticOutputParser(pydantic_object=ExtractionModel)
    
    # Initialize embeddings
    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL
        )
        logger.log_step("Embeddings Initialization", f"Using OpenAIEmbeddings with model {OPENAI_EMBEDDING_MODEL}")
    except ImportError:
        # Fall back to langchain_community if langchain_openai is not installed
        embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL
        )
        logger.log_step("Embeddings Initialization", f"Using deprecated OpenAIEmbeddings from langchain_community with model {OPENAI_EMBEDDING_MODEL}")
    
    # Initialize custom components
    temporal_normalizer = TemporalNormalizer(llm, logger)
    result_merger = ResultMerger(embedding_model=embeddings, logger=logger)
    output_formatter = OutputFormatter(logger)
    
    # Create extraction pipeline
    pipeline = ExtractionPipeline(
        document_loader=document_loader,
        text_splitter=text_splitter,
        llm=llm,
        output_parser=output_parser,
        temporal_normalizer=temporal_normalizer,
        result_merger=result_merger,
        output_formatter=output_formatter,
        max_concurrency=20,
        logger=logger
    )
    
    # Check if the example file exists, otherwise create it
    import os
    example_dir = "examples"
    example_file = os.path.join(example_dir, "medical_record.txt")
    
    if not os.path.exists(example_file):
        os.makedirs(example_dir, exist_ok=True)
        with open(example_file, "w") as f:
            f.write("""
Patient Medical Record
----------------------

Patient Information:
Name: John Smith
Date of Birth: 05/15/1980
Gender: Male
Medical Record Number: MRN-12345678

Medical History:
Allergies: Penicillin, Peanuts
Chronic Conditions: Type 2 Diabetes (diagnosed 2015), Hypertension (diagnosed 2018)

Current Medications:
1. Metformin 500mg, twice daily (for diabetes)
2. Lisinopril 10mg, once daily (for hypertension)
3. Aspirin 81mg, once daily (preventative)

Visit History:
-------------

Visit Date: 03/10/2023
Provider: Dr. Sarah Johnson
Assessment: Upper respiratory infection, likely viral
Plan: Rest, increased fluids, over-the-counter cough suppressant

Visit Date: 07/22/2023
Provider: Dr. Michael Chen
Assessment: Type 2 Diabetes - well controlled
Plan: Continue current medications, maintain diet and exercise regimen

Visit Date: 11/15/2023
Provider: Dr. Sarah Johnson
Assessment: Overall good health, mild hyperlipidemia
Plan: Dietary modifications to reduce cholesterol, continue current medications
""")
        logger.log_step("File Creation", f"Created example file: {example_file}")
    
    # Update document loader to TextLoader for the text file
    pipeline.document_loader = TextLoader
    
    # Process document
    logger.log_step("Processing", f"Processing document: {example_file}")
    result = await pipeline.process_document(
        document_path=example_file,
        fields=fields,
        domain="medical",
        output_formats=["json", "text", "xml"]
    )
    
    # Print results
    print("JSON Output:")
    print(json.dumps(result["json_output"], indent=2))
    
    print("\nText Output:")
    print(result["text_output"])
    
    if "xml_output" in result:
        print("\nXML Output (first 500 chars):")
        print(result["xml_output"][:500] + "...")
    
    print(f"\nProcessing Time: {result['metadata']['processing_time']:.2f} seconds")
    print(f"Chunk Count: {result['metadata']['chunk_count']}")
    print(f"Prompt Tokens: {result['metadata']['prompt_tokens']}")
    print(f"Completion Tokens: {result['metadata']['completion_tokens']}")
    print(f"Total Tokens: {result['metadata']['total_tokens']}")


if __name__ == "__main__":
    asyncio.run(main())
