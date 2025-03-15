"""
Parallel Extraction Pipeline for the Dudoxx Extraction system.

This module implements a parallel extraction pipeline that processes multiple
sub-domains in parallel for each document chunk.
"""

import asyncio
import time
import json
import concurrent.futures
import threading
from typing import List, Dict, Any, Optional, Set, Union
from pydantic import BaseModel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

# Import the configuration service
from dudoxx_extraction.configuration_service import ConfigurationService

# Local imports
from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition
from dudoxx_extraction.document_loaders.document_loader_factory import DocumentLoaderFactory
from dudoxx_extraction.extraction_pipeline import ResultMerger, TemporalNormalizer, OutputFormatter
from dudoxx_extraction.null_filter import DudoxxNullFilter, filter_extraction_result


class ParallelExtractionPipeline:
    """
    Parallel extraction pipeline for processing multiple sub-domains in parallel.
    
    This pipeline splits documents into chunks and processes multiple sub-domains
    in parallel for each chunk, then merges the results.
    """
    
    def __init__(
        self,
        llm=None,
        text_splitter=None,
        temporal_normalizer=None,
        result_merger=None,
        output_formatter=None,
        max_concurrency: int = 20
    ):
        """
        Initialize the parallel extraction pipeline.
        
        Args:
            llm: LangChain LLM
            text_splitter: LangChain text splitter
            temporal_normalizer: Temporal normalizer
            result_merger: Result merger
            output_formatter: Output formatter
            max_concurrency: Maximum concurrent LLM requests
        """
        # Initialize configuration service
        self.config_service = ConfigurationService()
        llm_config = self.config_service.get_llm_config()
        
        # Initialize LLM
        self.llm = llm or ChatOpenAI(
            base_url=llm_config["base_url"],
            api_key=llm_config["api_key"],
            model_name=llm_config["model_name"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"]
        )
        
        # Get extraction configuration
        extraction_config = self.config_service.get_extraction_config()
        
        # Initialize text splitter
        self.text_splitter = text_splitter or RecursiveCharacterTextSplitter(
            chunk_size=extraction_config["chunk_size"],
            chunk_overlap=extraction_config["chunk_overlap"],
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize other components
        self.temporal_normalizer = temporal_normalizer or TemporalNormalizer(self.llm)
        self.result_merger = result_merger or ResultMerger()
        self.output_formatter = output_formatter or OutputFormatter()
        
        # Set maximum concurrency from configuration if not provided
        self.max_concurrency = max_concurrency or extraction_config["max_concurrency"]
        
        # Get domain registry
        self.domain_registry = DomainRegistry()
        
        # Initialize console for rich logging
        self.console = Console()
    
    def process_document_with_threads(
        self,
        document_path: str,
        domain_name: str,
        sub_domain_names: Optional[List[str]] = None,
        output_formats: Optional[List[str]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a document through the parallel extraction pipeline using thread pool.
        
        Args:
            document_path: Path to document
            domain_name: Domain name
            sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        start_time = time.time()
        
        # Get domain definition
        domain = self.domain_registry.get_domain(domain_name)
        if domain is None:
            raise ValueError(f"Domain '{domain_name}' not found")
        
        # Determine sub-domains to process
        sub_domains = []
        if sub_domain_names:
            for name in sub_domain_names:
                sub_domain = domain.get_sub_domain(name)
                if sub_domain:
                    sub_domains.append(sub_domain)
                else:
                    self.console.print(f"[yellow]Warning:[/] Sub-domain '{name}' not found in domain '{domain_name}'")
        else:
            sub_domains = domain.sub_domains
        
        if not sub_domains:
            raise ValueError(f"No valid sub-domains found for domain '{domain_name}'")
        
        # Step 1: Load document
        loader = DocumentLoaderFactory.get_loader_for_file(document_path)
        if loader is None:
            raise ValueError(f"No loader available for file: {document_path}")
        
        documents = loader.load()
        
        # Step 2: Split document into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Step 3: Process chunks and sub-domains in parallel using ThreadPoolExecutor
        tasks = []
        for chunk in chunks:
            for sub_domain in sub_domains:
                tasks.append((chunk, sub_domain))
        
        # Try to import progress manager for progress updates
        has_progress_manager = False
        if request_id:
            try:
                from dudoxx_extraction_api.progress_manager import add_progress_update
                has_progress_manager = True
                
                # Send progress update
                add_progress_update(
                    request_id, 
                    "processing", 
                    f"Processing document with {len(chunks)} chunks and {len(sub_domains)} sub-domains...", 
                    30
                )
            except ImportError:
                self.console.print("[yellow]Warning: Progress manager not available, using local progress display[/]")
        
        # Create a progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[cyan]{task.fields[status]}"),
            console=self.console
        ) as progress:
            # Add a task for overall progress
            overall_task = progress.add_task(
                f"[green]Processing {len(chunks)} chunks with {len(sub_domains)} sub-domains...", 
                total=len(tasks),
                status="Starting"
            )
            
            # Create a dictionary to track sub-domain tasks
            subdomain_tasks = {}
            for sub_domain in sub_domains:
                subdomain_tasks[sub_domain.name] = progress.add_task(
                    f"[blue]Processing {sub_domain.name}...",
                    total=len(chunks),
                    status="Waiting"
                )
            
            # Process tasks in parallel using ThreadPoolExecutor
            extraction_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                # Submit all tasks to the executor
                future_to_task = {
                    executor.submit(self._process_chunk_subdomain, chunk, sub_domain): 
                    (chunk, sub_domain) for chunk, sub_domain in tasks
                }
                
                # Process completed tasks as they finish
                for future in concurrent.futures.as_completed(future_to_task):
                    chunk, sub_domain = future_to_task[future]
                    try:
                        result = future.result()
                        extraction_results.append(result)
                        
                        # Update progress
                        progress.update(overall_task, advance=1, status=f"Completed {len(extraction_results)}/{len(tasks)}")
                        progress.update(subdomain_tasks[sub_domain.name], advance=1, status="Processing")
                        
                    except Exception as e:
                        self.console.print(f"[red]Error processing chunk {chunks.index(chunk)} with sub-domain {sub_domain.name}: {e}[/]")
                        # Add empty result on error
                        extraction_results.append({
                            "chunk_index": chunks.index(chunk),
                            "sub_domain": sub_domain.name,
                            "result": {}
                        })
                        
                        # Update progress
                        progress.update(overall_task, advance=1, status=f"Error in task")
                        progress.update(subdomain_tasks[sub_domain.name], advance=1, status="Error")
            
            # Update all tasks to completed
            progress.update(overall_task, status="Completed")
            for task_id in subdomain_tasks.values():
                progress.update(task_id, status="Completed")
        
        # Step 4: Organize results by chunk and sub-domain
        chunk_results = {}
        for result in extraction_results:
            chunk_index = result["chunk_index"]
            sub_domain_name = result["sub_domain"]
            
            if chunk_index not in chunk_results:
                chunk_results[chunk_index] = {}
            
            chunk_results[chunk_index][sub_domain_name] = result["result"]
        
        # Step 5: Merge results from sub-domains for each chunk with improved tracking
        self.console.print("[green]Merging results from sub-domains...[/]")
        if has_progress_manager and request_id:
            add_progress_update(request_id, "processing", "Merging results from sub-domains...", 70)
        merged_chunk_results = []
        for chunk_index, sub_domain_results in chunk_results.items():
            merged_result = {}
            
            # Track source sub-domains for each field
            field_sources = {}
            field_confidences = {}
            
            for sub_domain_name, result in sub_domain_results.items():
                for field_name, value in result.items():
                    # Track field source
                    if field_name not in field_sources:
                        field_sources[field_name] = []
                        field_confidences[field_name] = []
                    
                    field_sources[field_name].append(sub_domain_name)
                    field_confidences[field_name].append(1.0)  # Default confidence
                    
                    # Update field value
                    if field_name not in merged_result:
                        # New field
                        merged_result[field_name] = value
                    elif merged_result[field_name] is None and value is not None:
                        # Replace null value with non-null
                        merged_result[field_name] = value
                    elif isinstance(merged_result[field_name], list) and isinstance(value, list):
                        # Merge lists
                        merged_result[field_name].extend(value)
                    # For other cases, keep the first value
            
            # Add metadata for tracking
            merged_result["_metadata"] = {
                "chunk_index": chunk_index,
                "source_subdomains": field_sources,
                "confidence": field_confidences
            }
            
            merged_chunk_results.append(merged_result)
        
        # Step 6: Normalize temporal data
        self.console.print("[green]Normalizing temporal data...[/]")
        if has_progress_manager and request_id:
            add_progress_update(request_id, "processing", "Normalizing temporal data...", 80)
        normalized_results = []
        for result in merged_chunk_results:
            normalized_result = {}
            
            # Preserve metadata
            if "_metadata" in result:
                normalized_result["_metadata"] = result["_metadata"]
            
            # Normalize fields
            for field, value in result.items():
                if field == "_metadata":
                    continue
                    
                if field.endswith("_date") or field == "date":
                    # Normalize date fields
                    normalized_result[field] = self.temporal_normalizer.normalize_date(value)
                elif field == "timeline" and isinstance(value, list):
                    # Normalize timeline
                    normalized_result[field] = self.temporal_normalizer.construct_timeline(value)
                else:
                    normalized_result[field] = value
            
            normalized_results.append(normalized_result)
        
        # Step 7: Merge and deduplicate results from all chunks with improved handling
        self.console.print("[green]Merging and deduplicating results...[/]")
        if has_progress_manager and request_id:
            add_progress_update(request_id, "processing", "Merging and deduplicating results...", 90)
        final_merged_result = self.result_merger.merge_results(normalized_results)
        
        # Step 8: Format output
        self.console.print("[green]Formatting output...[/]")
        if has_progress_manager and request_id:
            add_progress_update(request_id, "processing", "Formatting output...", 95)
        output = {}
        
        # Ensure output_formats is a list
        if output_formats is None:
            output_formats = ["json", "text"]
        
        # Create a null filter to remove null, N/A, and empty values
        null_filter = DudoxxNullFilter(
            remove_null=True,
            remove_na=True,
            remove_empty_strings=True,
            remove_zeros=False,
            preserve_metadata=True
        )
        
        # Apply null filter to the merged result
        filtered_result = null_filter.filter_result(final_merged_result)
        
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
            "sub_domain_count": len(sub_domains),
            "task_count": len(tasks),
            "token_count": self._estimate_token_count(chunks)
        }
        
        self.console.print(f"[green]Extraction completed in {processing_time:.2f} seconds[/]")
        
        return output
    
    def _process_chunk_subdomain(self, chunk, sub_domain):
        """
        Process a chunk with a sub-domain using the LLM.
        
        Args:
            chunk: Document chunk
            sub_domain: Sub-domain definition
            
        Returns:
            Extraction result
        """
        # Generate prompt
        prompt = self._generate_prompt(chunk.page_content, sub_domain)
        
        # Process with LLM (synchronous version)
        response = self.llm.generate([prompt])
        
        # Parse output
        try:
            parser = JsonOutputParser()
            parsed_output = parser.parse(response.generations[0][0].text)
            return {
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "sub_domain": sub_domain.name,
                "result": parsed_output
            }
        except Exception as e:
            self.console.print(f"[red]Error parsing output for sub-domain '{sub_domain.name}': {e}[/]")
            self.console.print(f"[yellow]Raw output: {response.generations[0][0].text}[/]")
            # Return empty result on parsing error
            return {
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "sub_domain": sub_domain.name,
                "result": {}
            }
    
    async def process_document(
        self,
        document_path: str,
        domain_name: str,
        sub_domain_names: Optional[List[str]] = None,
        output_formats: List[str] = ["json", "text"]
    ) -> Dict[str, Any]:
        """
        Process a document through the parallel extraction pipeline using asyncio.
        
        Args:
            document_path: Path to document
            domain_name: Domain name
            sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
            output_formats: Output formats to generate
            
        Returns:
            Extraction result
        """
        start_time = time.time()
        
        # Get domain definition
        domain = self.domain_registry.get_domain(domain_name)
        if domain is None:
            raise ValueError(f"Domain '{domain_name}' not found")
        
        # Determine sub-domains to process
        sub_domains = []
        if sub_domain_names:
            for name in sub_domain_names:
                sub_domain = domain.get_sub_domain(name)
                if sub_domain:
                    sub_domains.append(sub_domain)
                else:
                    print(f"Warning: Sub-domain '{name}' not found in domain '{domain_name}'")
        else:
            sub_domains = domain.sub_domains
        
        if not sub_domains:
            raise ValueError(f"No valid sub-domains found for domain '{domain_name}'")
        
        # Step 1: Load document
        loader = DocumentLoaderFactory.get_loader_for_file(document_path)
        if loader is None:
            raise ValueError(f"No loader available for file: {document_path}")
        
        documents = loader.load()
        
        # Step 2: Split document into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Step 3: Process chunks and sub-domains in parallel
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def process_chunk_subdomain(chunk, sub_domain):
            async with semaphore:
                # Generate prompt
                prompt = self._generate_prompt(chunk.page_content, sub_domain)
                
                # Process with LLM
                response = await self.llm.agenerate([prompt])
                
                # Parse output
                try:
                    parser = JsonOutputParser()
                    parsed_output = parser.parse(response.generations[0][0].text)
                    return {
                        "chunk_index": chunks.index(chunk),
                        "sub_domain": sub_domain.name,
                        "result": parsed_output
                    }
                except Exception as e:
                    print(f"Error parsing output for sub-domain '{sub_domain.name}': {e}")
                    print(f"Raw output: {response.generations[0][0].text}")
                    # Return empty result on parsing error
                    return {
                        "chunk_index": chunks.index(chunk),
                        "sub_domain": sub_domain.name,
                        "result": {}
                    }
        
        # Create tasks for all chunks and sub-domains
        tasks = []
        for chunk in chunks:
            for sub_domain in sub_domains:
                tasks.append(process_chunk_subdomain(chunk, sub_domain))
        
        # Execute tasks in parallel
        extraction_results = await asyncio.gather(*tasks)
        
        # Step 4: Organize results by chunk and sub-domain
        chunk_results = {}
        for result in extraction_results:
            chunk_index = result["chunk_index"]
            sub_domain_name = result["sub_domain"]
            
            if chunk_index not in chunk_results:
                chunk_results[chunk_index] = {}
            
            chunk_results[chunk_index][sub_domain_name] = result["result"]
        
        # Step 5: Merge results from sub-domains for each chunk with improved tracking
        merged_chunk_results = []
        for chunk_index, sub_domain_results in chunk_results.items():
            merged_result = {}
            
            # Track source sub-domains for each field
            field_sources = {}
            field_confidences = {}
            
            for sub_domain_name, result in sub_domain_results.items():
                for field_name, value in result.items():
                    # Track field source
                    if field_name not in field_sources:
                        field_sources[field_name] = []
                        field_confidences[field_name] = []
                    
                    field_sources[field_name].append(sub_domain_name)
                    field_confidences[field_name].append(1.0)  # Default confidence
                    
                    # Update field value
                    if field_name not in merged_result:
                        # New field
                        merged_result[field_name] = value
                    elif merged_result[field_name] is None and value is not None:
                        # Replace null value with non-null
                        merged_result[field_name] = value
                    elif isinstance(merged_result[field_name], list) and isinstance(value, list):
                        # Merge lists
                        merged_result[field_name].extend(value)
                    # For other cases, keep the first value
            
            # Add metadata for tracking
            merged_result["_metadata"] = {
                "chunk_index": chunk_index,
                "source_subdomains": field_sources,
                "confidence": field_confidences
            }
            
            merged_chunk_results.append(merged_result)
        
        # Step 6: Normalize temporal data
        normalized_results = []
        for result in merged_chunk_results:
            normalized_result = {}
            
            # Preserve metadata
            if "_metadata" in result:
                normalized_result["_metadata"] = result["_metadata"]
            
            # Normalize fields
            for field, value in result.items():
                if field == "_metadata":
                    continue
                    
                if field.endswith("_date") or field == "date":
                    # Normalize date fields
                    normalized_result[field] = self.temporal_normalizer.normalize_date(value)
                elif field == "timeline" and isinstance(value, list):
                    # Normalize timeline
                    normalized_result[field] = self.temporal_normalizer.construct_timeline(value)
                else:
                    normalized_result[field] = value
            
            normalized_results.append(normalized_result)
        
        # Step 7: Merge and deduplicate results from all chunks
        final_merged_result = self.result_merger.merge_results(normalized_results)
        
        # Step 8: Format output
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
        filtered_result = null_filter.filter_result(final_merged_result)
        
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
            "sub_domain_count": len(sub_domains),
            "task_count": len(tasks),
            "token_count": self._estimate_token_count(chunks)
        }
        
        return output
    
    def _generate_prompt(self, text: str, sub_domain: SubDomainDefinition) -> str:
        """
        Generate prompt for field extraction.
        
        Args:
            text: Text to extract from
            sub_domain: Sub-domain definition
            
        Returns:
            Prompt for LLM
        """
        # Use the PromptBuilder to generate a more comprehensive prompt
        try:
            from dudoxx_extraction.prompt_builder import PromptBuilder
            
            # Find the domain that contains this sub-domain
            domain_name = None
            for domain in self.domain_registry.get_all_domains():
                if domain.get_sub_domain(sub_domain.name):
                    domain_name = domain.name
                    break
            
            if domain_name:
                prompt_builder = PromptBuilder(self.domain_registry)
                return prompt_builder.build_extraction_prompt(
                    text=text,
                    domain_name=domain_name,
                    sub_domain_names=[sub_domain.name]
                )
        except (ValueError, ImportError) as e:
            # Fall back to the simple prompt generation if PromptBuilder fails
            self.console.print(f"[yellow]Warning: PromptBuilder failed, falling back to simple prompt: {e}[/]")
        
        # Fallback to original method if PromptBuilder fails
        # Get prompt text from sub-domain
        prompt_text = sub_domain.to_prompt_text()
        
        # Create prompt
        prompt = f"""{prompt_text}

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


# Synchronous wrapper for the parallel extraction pipeline
async def extract_document(
    document_path: str,
    domain_name: str,
    sub_domain_names: Optional[List[str]] = None,
    output_formats: List[str] = ["json", "text"]
) -> Dict[str, Any]:
    """
    Extract information from a document using the parallel extraction pipeline.
    
    Args:
        document_path: Path to document
        domain_name: Domain name
        sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
        output_formats: Output formats to generate
        
    Returns:
        Extraction result
    """
    pipeline = ParallelExtractionPipeline()
    return await pipeline.process_document(
        document_path=document_path,
        domain_name=domain_name,
        sub_domain_names=sub_domain_names,
        output_formats=output_formats
    )


def extract_document_sync(
    document_path: str,
    domain_name: str,
    sub_domain_names: Optional[List[str]] = None,
    output_formats: Optional[List[str]] = None,
    use_threads: bool = True,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract information from a document using the parallel extraction pipeline (synchronous version).
    
    Args:
        document_path: Path to document
        domain_name: Domain name
        sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
        output_formats: Output formats to generate
        use_threads: Whether to use thread-based parallelism (True) or asyncio-based parallelism (False)
        
    Returns:
        Extraction result
    """
    pipeline = ParallelExtractionPipeline()
    
    if use_threads:
        # Use thread-based parallelism
        return pipeline.process_document_with_threads(
            document_path=document_path,
            domain_name=domain_name,
            sub_domain_names=sub_domain_names,
            output_formats=output_formats,
            request_id=request_id
        )
    else:
        # Use asyncio-based parallelism
        import asyncio
        
        # Create a new event loop for each call to avoid issues with closed loops
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(pipeline.process_document(
                document_path=document_path,
                domain_name=domain_name,
                sub_domain_names=sub_domain_names,
                output_formats=output_formats
            ))
        finally:
            # Clean up the event loop
            loop.close()
