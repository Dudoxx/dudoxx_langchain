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
    from langchain.chains import LLMChain
except ImportError:
    try:
        from langchain_core.chains import LLMChain
    except ImportError:
        from langchain_community.chains import LLMChain
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
            # Initialize configuration service
            config_service = ConfigurationService()
            llm_config = config_service.get_llm_config()
            
            # Initialize ChatOpenAI with settings from configuration service
            self.llm = ChatOpenAI(
                base_url=llm_config["base_url"],
                api_key=llm_config["api_key"],
                model_name=llm_config["model_name"],
                temperature=llm_config["temperature"]
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


# Import the configuration service
from dudoxx_extraction.configuration_service import ConfigurationService

class ResultMerger:
    """Merges and deduplicates results from multiple chunks."""
    
    def __init__(self, embedding_model=None, deduplication_threshold=0.85):
        """
        Initialize with embedding model for deduplication.
        
        Args:
            embedding_model: LangChain embedding model
            deduplication_threshold: Similarity threshold for deduplication (lowered from 0.9 to 0.85 for better deduplication)
        """
        # Use the embedding model from configuration service
        if embedding_model is None:
            # Initialize configuration service
            config_service = ConfigurationService()
            embedding_config = config_service.get_embedding_config()
            
            try:
                # Try to import from langchain_openai (recommended)
                from langchain_openai import OpenAIEmbeddings
                self.embedding_model = OpenAIEmbeddings(
                    model=embedding_config["model"],
                    api_key=embedding_config["api_key"],
                    base_url=embedding_config["base_url"]
                )
            except ImportError:
                # Fall back to langchain_community if langchain_openai is not installed
                self.embedding_model = OpenAIEmbeddings(
                    model=embedding_config["model"],
                    openai_api_key=embedding_config["api_key"],
                    openai_api_base=embedding_config["base_url"]
                )
        else:
            self.embedding_model = embedding_model
        self.deduplication_threshold = deduplication_threshold
        
        # Define priority fields that should be preserved even if null in some chunks
        self.priority_fields = [
            "patient_name", "date_of_birth", "gender", "medical_record_number",
            "full_name", "name", "first_name", "last_name"
        ]
        
        # Define field groups for merging related fields
        self.field_groups = {
            "name_fields": ["patient_name", "full_name", "name", "first_name", "last_name"],
            "date_fields": ["date_of_birth", "birth_date", "dob"],
            "id_fields": ["medical_record_number", "mrn", "id", "patient_id"]
        }
    
    def merge_results(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge results from multiple chunks with improved handling of key fields.
        
        Args:
            chunk_results: List of results from chunks
            
        Returns:
            Merged and deduplicated result
        """
        if not chunk_results:
            return {"_metadata": {"source_chunks": {}, "confidence": {}}}
        
        merged_fields = {}
        field_sources = {}
        field_confidences = {}
        field_non_null_values = {}  # Track non-null values for each field
        
        # First pass: Collect all field values and track non-null values
        for i, result in enumerate(chunk_results):
            for field_name, value in result.items():
                if field_name.startswith("_"):
                    # Skip metadata fields in the first pass
                    continue
                    
                if field_name not in merged_fields:
                    merged_fields[field_name] = []
                    field_sources[field_name] = []
                    field_confidences[field_name] = []
                    field_non_null_values[field_name] = []
                
                merged_fields[field_name].append(value)
                field_sources[field_name].append(i)
                
                # Get confidence from metadata if available, otherwise default to 1.0
                confidence = 1.0
                if "_metadata" in result and "confidence" in result["_metadata"]:
                    field_confidence = result["_metadata"]["confidence"].get(field_name)
                    if field_confidence and isinstance(field_confidence, list) and len(field_confidence) > 0:
                        confidence = field_confidence[0]
                
                field_confidences[field_name].append(confidence)
                
                # Track non-null values
                if value is not None and value != "":
                    field_non_null_values[field_name].append((i, value, confidence))
        
        # Second pass: Merge and deduplicate fields
        final_result = {}
        for field_name, values in merged_fields.items():
            # Check if this field has any non-null values
            non_null_values = field_non_null_values.get(field_name, [])
            
            if not non_null_values:
                # No non-null values, check if this is a priority field
                if field_name in self.priority_fields:
                    # For priority fields, keep null value to maintain schema
                    final_result[field_name] = None
                # Otherwise, skip this field
                continue
            
            # Check if this field belongs to a field group
            field_group = None
            for group_name, group_fields in self.field_groups.items():
                if field_name in group_fields:
                    field_group = group_name
                    break
            
            # If field is part of a group, check for values in related fields
            if field_group:
                # Collect all non-null values from related fields
                related_values = []
                for related_field in self.field_groups[field_group]:
                    if related_field in field_non_null_values:
                        related_values.extend(field_non_null_values[related_field])
                
                # If we have related values and this field has no values, use them for this field
                if related_values and not non_null_values:
                    # Sort by confidence
                    related_values.sort(key=lambda x: x[2], reverse=True)
                    # Use the highest confidence value
                    final_result[field_name] = related_values[0][1]
                    continue
            
            # Handle based on value type
            if len(non_null_values) == 1:
                # Only one non-null value, use it directly
                final_result[field_name] = non_null_values[0][1]
            else:
                # Multiple non-null values, need to merge/deduplicate
                if all(isinstance(val[1], list) for val in non_null_values):
                    # Field is a list in all chunks, merge all items and deduplicate
                    all_items = []
                    for _, value, _ in non_null_values:
                        if value:  # Check if value is not None or empty
                            all_items.extend(value)
                    
                    # Deduplicate the merged list
                    final_result[field_name] = self._deduplicate_list(all_items)
                elif all(isinstance(val[1], dict) for val in non_null_values):
                    # Field is a dictionary in all chunks, merge by keys with confidence weighting
                    merged_dict = self._merge_dictionaries([value for _, value, _ in non_null_values], 
                                                          [conf for _, _, conf in non_null_values])
                    final_result[field_name] = merged_dict
                else:
                    # Field is a single value or mixed types, choose the most confident one
                    # Sort by confidence
                    non_null_values.sort(key=lambda x: x[2], reverse=True)
                    final_result[field_name] = non_null_values[0][1]
        
        # Preserve metadata from all chunks
        combined_metadata = {"source_chunks": {}, "confidence": {}}
        
        # Combine metadata from all chunks
        for i, result in enumerate(chunk_results):
            if "_metadata" in result:
                # Add source chunks
                if "source_chunks" in result["_metadata"]:
                    for field, sources in result["_metadata"]["source_chunks"].items():
                        if field not in combined_metadata["source_chunks"]:
                            combined_metadata["source_chunks"][field] = []
                        combined_metadata["source_chunks"][field].extend(sources)
                
                # Add confidence values
                if "confidence" in result["_metadata"]:
                    for field, confidences in result["_metadata"]["confidence"].items():
                        if field not in combined_metadata["confidence"]:
                            combined_metadata["confidence"][field] = []
                        combined_metadata["confidence"][field].extend(confidences)
        
        # Add field sources and confidences from this merge operation
        for field, sources in field_sources.items():
            combined_metadata["source_chunks"][field] = sources
        
        for field, confidences in field_confidences.items():
            combined_metadata["confidence"][field] = confidences
        
        # Add list of merged fields
        combined_metadata["merged_fields"] = list(field_non_null_values.keys())
        
        # Add metadata to final result
        final_result["_metadata"] = combined_metadata
        
        return final_result
    
    def _merge_dictionaries(self, dicts: List[Dict[str, Any]], confidences: List[float]) -> Dict[str, Any]:
        """
        Merge dictionaries with confidence weighting.
        
        Args:
            dicts: List of dictionaries to merge
            confidences: Confidence scores for each dictionary
            
        Returns:
            Merged dictionary
        """
        if not dicts:
            return {}
        
        # Initialize with first dictionary
        result = dicts[0].copy()
        
        # Merge remaining dictionaries
        for i, d in enumerate(dicts[1:], 1):
            for key, value in d.items():
                if key not in result:
                    # New key, add it
                    result[key] = value
                elif result[key] is None and value is not None:
                    # Replace null value with non-null
                    result[key] = value
                elif isinstance(result[key], list) and isinstance(value, list):
                    # Merge lists
                    result[key].extend(value)
                    result[key] = self._deduplicate_list(result[key])
                elif confidences[i] > confidences[0]:
                    # Higher confidence, replace value
                    result[key] = value
        
        return result
    
    def _deduplicate_list(self, items: List[Any]) -> List[Any]:
        """
        Deduplicate a list of items using embeddings for text and equality for other types.
        
        Args:
            items: List of items to deduplicate
            
        Returns:
            Deduplicated list
        """
        if not items:
            return []
        
        # Handle empty or None items
        items = [item for item in items if item is not None and (not isinstance(item, str) or item.strip())]
        
        if not items:
            return []
        
        if all(isinstance(item, str) for item in items):
            # Text items, use embeddings for deduplication
            unique_items = []
            
            # Create vector store with first item
            try:
                vector_store = FAISS.from_texts([items[0]], self.embedding_model)
                unique_items.append(items[0])
                
                # Check each item against vector store
                for item in items[1:]:
                    # Skip very short items (likely noise)
                    if len(item.strip()) < 3:
                        continue
                        
                    results = vector_store.similarity_search_with_score(item, k=1)
                    
                    if not results or results[0][1] > self.deduplication_threshold:
                        # Item is unique, add to vector store and unique items
                        vector_store.add_texts([item])
                        unique_items.append(item)
                
                return unique_items
            except Exception as e:
                # Fall back to simple deduplication if embedding fails
                print(f"Warning: Embedding-based deduplication failed: {e}")
                return list(set(items))
        elif all(isinstance(item, dict) for item in items):
            # For dictionaries, deduplicate by serializing to JSON
            unique_items = []
            seen_json = set()
            
            for item in items:
                item_json = json.dumps(item, sort_keys=True)
                if item_json not in seen_json:
                    seen_json.add(item_json)
                    unique_items.append(item)
            
            return unique_items
        else:
            # Non-text items, use equality for deduplication
            # This works for numbers, booleans, and other hashable types
            try:
                return list(set(items))
            except TypeError:
                # Fall back for unhashable types
                unique_items = []
                for item in items:
                    if item not in unique_items:
                        unique_items.append(item)
                return unique_items


# Import the null filter
from dudoxx_extraction.null_filter import DudoxxNullFilter, filter_extraction_result

class OutputFormatter:
    """Formats extraction results in different formats."""
    
    def __init__(self, apply_null_filter: bool = False, null_filter: Optional[DudoxxNullFilter] = None):
        """
        Initialize the output formatter.
        
        Args:
            apply_null_filter: Whether to apply null filtering by default
            null_filter: Custom null filter instance (if None, a default one will be created)
        """
        self.apply_null_filter = apply_null_filter
        self.null_filter = null_filter or DudoxxNullFilter()
    
    def format_json(self, merged_result: Dict[str, Any], include_metadata: bool = True, apply_null_filter: Optional[bool] = None) -> Dict[str, Any]:
        """
        Format result as JSON.
        
        Args:
            merged_result: Merged extraction result
            include_metadata: Whether to include metadata
            apply_null_filter: Whether to apply null filtering (overrides default setting)
            
        Returns:
            Formatted JSON result
        """
        result = merged_result.copy()
        
        # Apply null filtering if requested
        should_filter = self.apply_null_filter if apply_null_filter is None else apply_null_filter
        if should_filter:
            # Preserve metadata if requested
            preserve_fields = []
            if include_metadata:
                preserve_fields = [key for key in result if key.startswith("_")]
            
            result = self.null_filter.filter_result(result)
        
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
        # Initialize configuration service
        self.config_service = ConfigurationService()
        
        self.document_loader = document_loader or TextLoader
        
        # Get extraction configuration
        extraction_config = self.config_service.get_extraction_config()
        
        self.text_splitter = text_splitter or RecursiveCharacterTextSplitter(
            chunk_size=extraction_config["chunk_size"],
            chunk_overlap=extraction_config["chunk_overlap"],
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Get LLM configuration
        llm_config = self.config_service.get_llm_config()
        
        # Initialize ChatOpenAI with settings from configuration service
        self.llm = llm or ChatOpenAI(
            base_url=llm_config["base_url"],
            api_key=llm_config["api_key"],
            model_name=llm_config["model_name"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"]
        )
        
        self.output_parser = output_parser
        self.temporal_normalizer = temporal_normalizer or TemporalNormalizer(self.llm)
        self.result_merger = result_merger or ResultMerger()
        self.output_formatter = output_formatter or OutputFormatter()
        self.max_concurrency = max_concurrency or extraction_config["max_concurrency"]
    
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
        
        # Create a null filter to remove null, N/A, and empty values
        null_filter = DudoxxNullFilter(
            remove_null=True,
            remove_na=True,
            remove_empty_strings=True,
            remove_zeros=False,
            preserve_metadata=True
        )
        
        # Apply null filter to the merged result
        filtered_result = null_filter.filter_result(merged_result)
        
        # Format the filtered result
        if "json" in output_formats:
            output["json_output"] = self.output_formatter.format_json(filtered_result)
        
        if "text" in output_formats:
            output["text_output"] = self.output_formatter.format_text(filtered_result)
            
        if "xml" in output_formats:
            output["xml_output"] = self.output_formatter.format_xml(filtered_result)
        
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
        # Use the common prompt generator
        from dudoxx_extraction.prompt_generator import generate_extraction_prompt
        
        # Generate the prompt
        return generate_extraction_prompt(
            text=text,
            domain_name=domain,
            field_names=fields,
            domain_registry=self.config_service.get_domain_registry() if hasattr(self, 'config_service') else None
        )
    
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
    output_formats: List[str] = ["json", "text"],
    use_query_preprocessor: bool = True
) -> Dict[str, Any]:
    """
    Extract information from text using OpenAI LLM.
    
    Args:
        text: Text to extract information from
        fields: List of fields to extract
        domain: Domain context (e.g., "medical", "legal")
        output_formats: List of output formats (e.g., ["json", "text"])
        use_query_preprocessor: Whether to use query preprocessing
        
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
    
    # Preprocess the query if enabled
    if use_query_preprocessor:
        try:
            # Create a query from fields and domain
            query = f"Extract {', '.join(fields)} from {domain} document"
            
            # Import query preprocessor
            from dudoxx_extraction.query_preprocessor import QueryPreprocessor
            
            # Initialize query preprocessor with the same LLM configuration
            config_service = ConfigurationService()
            llm_config = config_service.get_llm_config()
            
            llm = ChatOpenAI(
                base_url=llm_config["base_url"],
                api_key=llm_config["api_key"],
                model_name=llm_config["model_name"],
                temperature=0.0,  # Use 0 temperature for deterministic results
                max_tokens=llm_config["max_tokens"]
            )
            
            query_preprocessor = QueryPreprocessor(llm=llm, use_rich_logging=True)
            
            try:
                # Preprocess query
                preprocessed_query = query_preprocessor.preprocess_query(query)
            except Exception as e:
                print(f"Error in query preprocessing: {e}")
                print("Falling back to original query")
                preprocessed_query = None
            
            # Use preprocessed information if available and confidence is high enough
            if preprocessed_query and preprocessed_query.confidence >= 0.7:
                # If domain is identified with high confidence, use it
                if preprocessed_query.identified_domain:
                    domain = preprocessed_query.identified_domain
                    print(f"Using preprocessed domain: {domain}")
                
                # If fields are identified with high confidence, use them
                if preprocessed_query.identified_fields:
                    fields = preprocessed_query.identified_fields
                    print(f"Using preprocessed fields: {', '.join(fields)}")
        except Exception as e:
            # Log error and continue with original query
            print(f"Error using query preprocessor: {e}")
            print("Continuing with original query")
    
    # Initialize configuration service
    config_service = ConfigurationService()
    llm_config = config_service.get_llm_config()
    
    # Initialize ChatOpenAI with settings from configuration service
    llm = ChatOpenAI(
        base_url=llm_config["base_url"],
        api_key=llm_config["api_key"],
        model_name=llm_config["model_name"],
        temperature=llm_config["temperature"],
        max_tokens=llm_config["max_tokens"]
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
                # Handle list of strings or other types
                text_output += f"{field.replace('_', ' ').title()}: {', '.join([str(item) for item in value])}\n"
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
    
    # Create a null filter to remove null, N/A, and empty values
    null_filter = DudoxxNullFilter(
        remove_null=True,
        remove_na=True,
        remove_empty_strings=True,
        remove_zeros=False,
        preserve_metadata=True
    )
    
    # Apply null filter to the result
    filtered_json_output = null_filter.filter_result(json_output)
    
    # Create text output from filtered result
    filtered_text_output = ""
    for field, value in filtered_json_output.items():
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                # Handle list of dictionaries (e.g., visits)
                filtered_text_output += f"\n{field.replace('_', ' ').title()}:\n"
                for item in value:
                    item_str = ", ".join([f"{k}: {v}" for k, v in item.items()])
                    filtered_text_output += f"- {item_str}\n"
            else:
                # Handle list of strings or other types
                filtered_text_output += f"{field.replace('_', ' ').title()}: {', '.join([str(item) for item in value])}\n"
        elif isinstance(value, dict):
            # Handle dictionary
            filtered_text_output += f"{field.replace('_', ' ').title()}:\n"
            for k, v in value.items():
                filtered_text_output += f"- {k}: {v}\n"
        else:
            # Handle simple value
            filtered_text_output += f"{field.replace('_', ' ').title()}: {value}\n"
    
    # Create result
    result = {
        "json_output": filtered_json_output,
        "text_output": filtered_text_output,
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
    output_formats: List[str] = ["json", "text"],
    use_query_preprocessor: bool = True
) -> Dict[str, Any]:
    """
    Extract information from a file.
    
    Args:
        file_path: Path to the file
        fields: List of fields to extract
        domain: Domain context (e.g., "medical", "legal")
        output_formats: List of output formats (e.g., ["json", "text"])
        use_query_preprocessor: Whether to use query preprocessing
        
    Returns:
        Dictionary with extraction results
    """
    # Just call extract_text with the file contents
    with open(file_path, "r") as f:
        text = f.read()
    
    return extract_text(text, fields, domain, output_formats, use_query_preprocessor)
