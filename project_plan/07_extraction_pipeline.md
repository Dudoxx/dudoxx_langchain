# Extraction Pipeline Controller

## Business Description

The Extraction Pipeline Controller is the central orchestrator of the entire extraction process. It coordinates the flow of data through all components of the system, from document chunking to output formatting. This component manages the execution of the pipeline, handles dependencies between components, and ensures that the extraction process runs efficiently and reliably.

The Extraction Pipeline Controller is designed to:
- Coordinate the end-to-end extraction process
- Manage the flow of data between components
- Handle asynchronous processing of document chunks
- Monitor the progress and performance of the extraction
- Provide a unified interface for client applications

## Dependencies

- **Document Chunker**: For segmenting large documents
- **Parallel LLM Processor**: For processing chunks concurrently
- **Field Extractor**: For extracting fields from chunks
- **Temporal Normalizer**: For normalizing temporal data
- **Result Merger & Deduplicator**: For merging results from multiple chunks
- **Output Formatter**: For generating structured outputs
- **Configuration Service**: For pipeline configuration
- **Logging Service**: For tracking pipeline execution
- **Error Handling Service**: For managing exceptions during processing

## Contracts

### Input
```python
class ExtractionRequest:
    document: str  # The full text to process
    fields: List[str]  # Fields to extract
    domain: str  # Domain context (e.g., "medical", "legal")
    output_formats: List[str] = ["json", "text"]  # Desired output formats
    config_overrides: Dict[str, Any] = {}  # Optional configuration overrides
```

### Output
```python
class ExtractionResult:
    json_output: Optional[Dict[str, Any]] = None  # Structured JSON output
    text_output: Optional[str] = None  # Flat text output
    xml_output: Optional[str] = None  # XML output if requested
    metadata: Dict[str, Any]  # Processing metadata including:
        # - processing_time: float  # Total processing time
        # - chunk_count: int  # Number of chunks processed
        # - token_count: int  # Total tokens processed
        # - warnings: List[str]  # Any warnings or issues
```

## Core Classes

### ExtractionPipeline
```python
from typing import Dict, Any, List, Optional
import time
import asyncio

class ExtractionPipeline:
    """Main pipeline controller for extraction process."""
    
    def __init__(self, chunker: DocumentChunker,
                processor: ParallelProcessor,
                extractor: FieldExtractor,
                normalizer: TemporalNormalizer,
                merger: ResultMerger,
                output_manager: OutputManager,
                config_service: ConfigurationService,
                logger: LoggingService,
                error_handler: ErrorHandlingService):
        """
        Initialize with all pipeline components.
        
        Args:
            chunker: For document chunking
            processor: For parallel processing
            extractor: For field extraction
            normalizer: For temporal normalization
            merger: For result merging
            output_manager: For output formatting
            config_service: For configuration
            logger: For logging
            error_handler: For error handling
        """
        self.chunker = chunker
        self.processor = processor
        self.extractor = extractor
        self.normalizer = normalizer
        self.merger = merger
        self.output_manager = output_manager
        self.config_service = config_service
        self.logger = logger
        self.error_handler = error_handler
    
    async def process_document(self, request: ExtractionRequest) -> ExtractionResult:
        """
        Process document through the extraction pipeline.
        
        Args:
            request: Extraction request
            
        Returns:
            Extraction result
        """
        start_time = time.time()
        warnings = []
        
        try:
            # Get domain configuration
            domain_config = self.config_service.get_domain_config(request.domain)
            
            # Apply config overrides
            if request.config_overrides:
                domain_config = self._apply_config_overrides(
                    domain_config, request.config_overrides
                )
            
            # Log start of processing
            self.logger.log_info(
                f"Starting extraction for domain: {request.domain}",
                {"document_length": len(request.document), "field_count": len(request.fields)}
            )
            
            # Step 1: Chunk document
            self.logger.log_info("Chunking document")
            chunks = await self._chunk_document(request.document, domain_config)
            
            # Log chunking results
            self.logger.log_info(
                f"Document split into {len(chunks)} chunks",
                {"chunk_count": len(chunks)}
            )
            
            # Step 2: Process chunks in parallel
            self.logger.log_info("Processing chunks in parallel")
            processed_chunks = await self._process_chunks(
                chunks, request.fields, domain_config
            )
            
            # Log processing results
            self.logger.log_info(
                f"Processed {len(processed_chunks)}/{len(chunks)} chunks successfully",
                {"success_count": len(processed_chunks), "total_chunks": len(chunks)}
            )
            
            # Check if any chunks failed
            if len(processed_chunks) < len(chunks):
                warnings.append(f"{len(chunks) - len(processed_chunks)} chunks failed to process")
            
            # Step 3: Normalize temporal data
            self.logger.log_info("Normalizing temporal data")
            normalized_chunks = await self._normalize_temporal_data(
                processed_chunks, domain_config
            )
            
            # Step 4: Merge results
            self.logger.log_info("Merging results")
            merged_result = await self._merge_results(
                normalized_chunks, request.fields, domain_config
            )
            
            # Step 5: Format output
            self.logger.log_info("Formatting output")
            formatted_output = await self._format_output(
                merged_result, request.output_formats, domain_config
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create result
            result = ExtractionResult(
                json_output=formatted_output.json_output,
                text_output=formatted_output.text_output,
                xml_output=formatted_output.xml_output,
                metadata={
                    "processing_time": processing_time,
                    "chunk_count": len(chunks),
                    "token_count": self._calculate_total_tokens(processed_chunks),
                    "warnings": warnings
                }
            )
            
            # Log completion
            self.logger.log_info(
                f"Extraction completed in {processing_time:.2f} seconds",
                {"processing_time": processing_time}
            )
            
            return result
            
        except Exception as e:
            # Handle exceptions
            processing_time = time.time() - start_time
            
            # Log error
            self.logger.log_error(
                f"Extraction failed: {str(e)}",
                {"error": str(e), "processing_time": processing_time}
            )
            
            # Handle error
            self.error_handler.handle_pipeline_error(e, request)
            
            # Return partial result if possible
            return ExtractionResult(
                metadata={
                    "processing_time": processing_time,
                    "error": str(e),
                    "warnings": warnings
                }
            )
    
    async def _chunk_document(self, document: str, 
                            domain_config: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Chunk document using appropriate strategy.
        
        Args:
            document: Document to chunk
            domain_config: Domain configuration
            
        Returns:
            List of document chunks
        """
        try:
            chunking_config = domain_config.get("chunking", {})
            
            return self.chunker.chunk_document(
                document=document,
                domain=domain_config.get("name"),
                max_chunk_size=chunking_config.get("max_chunk_size", 16000),
                overlap_size=chunking_config.get("overlap_size", 200)
            )
        except Exception as e:
            # Handle chunking errors
            self.error_handler.handle_chunking_error(e, document)
            raise
    
    async def _process_chunks(self, chunks: List[DocumentChunk],
                            fields: List[str],
                            domain_config: Dict[str, Any]) -> List[ExtractedFields]:
        """
        Process chunks in parallel.
        
        Args:
            chunks: Document chunks
            fields: Fields to extract
            domain_config: Domain configuration
            
        Returns:
            List of extracted fields
        """
        try:
            # Get field definitions
            field_definitions = self.config_service.get_field_definitions(
                domain_config.get("name"), fields
            )
            
            # Get processing config
            processing_config = domain_config.get("processing", {})
            
            # Define chunk processing function
            async def process_chunk(chunk: DocumentChunk) -> ExtractedFields:
                return await self.extractor.extract_fields(
                    chunk=chunk,
                    field_definitions=field_definitions,
                    domain=domain_config.get("name"),
                    examples=processing_config.get("examples")
                )
            
            # Process chunks in parallel
            return await self.processor.process_chunks(
                chunks=chunks,
                processor_func=process_chunk,
                retry_attempts=processing_config.get("retry_attempts", 3)
            )
        except Exception as e:
            # Handle processing errors
            self.error_handler.handle_processing_error(e, chunks)
            raise
    
    async def _normalize_temporal_data(self, extracted_chunks: List[ExtractedFields],
                                     domain_config: Dict[str, Any]) -> List[ExtractedFields]:
        """
        Normalize temporal data in extracted chunks.
        
        Args:
            extracted_chunks: Extracted fields from chunks
            domain_config: Domain configuration
            
        Returns:
            Normalized extracted fields
        """
        try:
            # Get temporal fields
            temporal_fields = [
                f["name"] for f in self.config_service.get_field_definitions(
                    domain_config.get("name")
                ) if f.get("type") == "date"
            ]
            
            if not temporal_fields:
                # No temporal fields to normalize
                return extracted_chunks
                
            # Get timeline configuration
            timeline_config = domain_config.get("timeline")
            
            # Normalize each chunk
            normalized_chunks = []
            
            for chunk in extracted_chunks:
                # Normalize temporal data
                normalized_data = self.normalizer.normalize(
                    extracted_data=chunk.fields,
                    temporal_fields=temporal_fields,
                    timeline_config=timeline_config
                )
                
                # Create new chunk with normalized data
                normalized_chunk = ExtractedFields(
                    chunk_index=chunk.chunk_index,
                    fields=normalized_data.data,
                    confidence=chunk.confidence,
                    metadata={
                        **chunk.metadata,
                        "normalization": normalized_data.metadata
                    }
                )
                
                normalized_chunks.append(normalized_chunk)
            
            return normalized_chunks
        except Exception as e:
            # Handle normalization errors
            self.error_handler.handle_normalization_error(e, extracted_chunks)
            raise
    
    async def _merge_results(self, normalized_chunks: List[ExtractedFields],
                           fields: List[str],
                           domain_config: Dict[str, Any]) -> MergedResult:
        """
        Merge results from multiple chunks.
        
        Args:
            normalized_chunks: Normalized extracted fields
            fields: Fields to extract
            domain_config: Domain configuration
            
        Returns:
            Merged result
        """
        try:
            # Get field definitions
            field_definitions = self.config_service.get_field_definitions(
                domain_config.get("name"), fields
            )
            
            # Merge results
            return self.merger.merge_results(
                extracted_chunks=normalized_chunks,
                field_definitions=field_definitions
            )
        except Exception as e:
            # Handle merging errors
            self.error_handler.handle_merging_error(e, normalized_chunks)
            raise
    
    async def _format_output(self, merged_result: MergedResult,
                           output_formats: List[str],
                           domain_config: Dict[str, Any]) -> FormattedOutput:
        """
        Format output in requested formats.
        
        Args:
            merged_result: Merged result
            output_formats: Desired output formats
            domain_config: Domain configuration
            
        Returns:
            Formatted output
        """
        try:
            # Get formatter options
            formatter_options = domain_config.get("formatters", {})
            
            # Format output
            return self.output_manager.format_output(
                merged_result=merged_result,
                output_formats=output_formats,
                include_metadata=True,
                formatter_options=formatter_options
            )
        except Exception as e:
            # Handle formatting errors
            self.error_handler.handle_formatting_error(e, merged_result)
            raise
    
    def _apply_config_overrides(self, base_config: Dict[str, Any],
                              overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply configuration overrides.
        
        Args:
            base_config: Base configuration
            overrides: Configuration overrides
            
        Returns:
            Updated configuration
        """
        # Deep copy to avoid modifying original
        config = copy.deepcopy(base_config)
        
        # Apply overrides
        for key, value in overrides.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                # Recursively update nested dictionaries
                config[key] = self._apply_config_overrides(config[key], value)
            else:
                # Replace value
                config[key] = value
        
        return config
    
    def _calculate_total_tokens(self, processed_chunks: List[ExtractedFields]) -> int:
        """
        Calculate total tokens processed.
        
        Args:
            processed_chunks: Processed chunks
            
        Returns:
            Total token count
        """
        total_tokens = 0
        
        for chunk in processed_chunks:
            # Get token usage from metadata
            metadata = chunk.metadata.get("processing_metadata", {})
            token_usage = metadata.get("token_usage", {})
            
            # Add prompt and completion tokens
            total_tokens += token_usage.get("prompt_tokens", 0)
            total_tokens += token_usage.get("completion_tokens", 0)
        
        return total_tokens
```

### PipelineFactory
```python
from typing import Dict, Any, Optional

class PipelineFactory:
    """Factory for creating extraction pipelines."""
    
    def __init__(self, config_service: ConfigurationService,
                logger: LoggingService,
                error_handler: ErrorHandlingService):
        """
        Initialize with services.
        
        Args:
            config_service: For configuration
            logger: For logging
            error_handler: For error handling
        """
        self.config_service = config_service
        self.logger = logger
        self.error_handler = error_handler
    
    def create_pipeline(self, config: Optional[Dict[str, Any]] = None) -> ExtractionPipeline:
        """
        Create extraction pipeline.
        
        Args:
            config: Optional configuration overrides
            
        Returns:
            Configured extraction pipeline
        """
        # Get base configuration
        base_config = self.config_service.get_global_config()
        
        # Apply overrides
        if config:
            for key, value in config.items():
                base_config[key] = value
        
        # Create components
        chunker = self._create_chunker(base_config.get("chunking", {}))
        processor = self._create_processor(base_config.get("processing", {}))
        extractor = self._create_extractor(base_config.get("extraction", {}))
        normalizer = self._create_normalizer(base_config.get("normalization", {}))
        merger = self._create_merger(base_config.get("merging", {}))
        output_manager = self._create_output_manager(base_config.get("formatting", {}))
        
        # Create pipeline
        return ExtractionPipeline(
            chunker=chunker,
            processor=processor,
            extractor=extractor,
            normalizer=normalizer,
            merger=merger,
            output_manager=output_manager,
            config_service=self.config_service,
            logger=self.logger,
            error_handler=self.error_handler
        )
    
    def _create_chunker(self, config: Dict[str, Any]) -> DocumentChunker:
        """Create document chunker."""
        # Implementation details
        pass
    
    def _create_processor(self, config: Dict[str, Any]) -> ParallelProcessor:
        """Create parallel processor."""
        # Implementation details
        pass
    
    def _create_extractor(self, config: Dict[str, Any]) -> FieldExtractor:
        """Create field extractor."""
        # Implementation details
        pass
    
    def _create_normalizer(self, config: Dict[str, Any]) -> TemporalNormalizer:
        """Create temporal normalizer."""
        # Implementation details
        pass
    
    def _create_merger(self, config: Dict[str, Any]) -> ResultMerger:
        """Create result merger."""
        # Implementation details
        pass
    
    def _create_output_manager(self, config: Dict[str, Any]) -> OutputManager:
        """Create output manager."""
        # Implementation details
        pass
```

### ExtractionService
```python
from typing import Dict, Any, Optional
import asyncio

class ExtractionService:
    """Service for handling extraction requests."""
    
    def __init__(self, pipeline_factory: PipelineFactory,
                config_service: ConfigurationService,
                logger: LoggingService,
                error_handler: ErrorHandlingService):
        """
        Initialize with factory and services.
        
        Args:
            pipeline_factory: For creating pipelines
            config_service: For configuration
            logger: For logging
            error_handler: For error handling
        """
        self.pipeline_factory = pipeline_factory
        self.config_service = config_service
        self.logger = logger
        self.error_handler = error_handler
        
        # Cache for domain-specific pipelines
        self.pipeline_cache = {}
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
        Process extraction request.
        
        Args:
            request: Extraction request
            
        Returns:
            Extraction result
        """
        try:
            # Get or create pipeline for domain
            pipeline = self._get_pipeline_for_domain(request.domain)
            
            # Process document
            return await pipeline.process_document(request)
        except Exception as e:
            # Handle service-level errors
            self.logger.log_error(
                f"Extraction service error: {str(e)}",
                {"error": str(e)}
            )
            
            self.error_handler.handle_service_error(e, request)
            
            # Return error result
            return ExtractionResult(
                metadata={
                    "error": str(e)
                }
            )
    
    def _get_pipeline_for_domain(self, domain: str) -> ExtractionPipeline:
        """
        Get or create pipeline for domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Extraction pipeline
        """
        if domain not in self.pipeline_cache:
            # Get domain-specific configuration
            domain_config = self.config_service.get_domain_config(domain)
            
            # Create pipeline
            self.pipeline_cache[domain] = self.pipeline_factory.create_pipeline(
                config=domain_config
            )
        
        return self.pipeline_cache[domain]
```

## Features to Implement

1. **Pipeline Orchestration**
   - End-to-end coordination of extraction process
   - Asynchronous processing for improved performance
   - Progress tracking and monitoring
   - Graceful error handling and recovery

2. **Configuration Management**
   - Domain-specific pipeline configuration
   - Runtime configuration overrides
   - Component-specific settings
   - Configuration validation

3. **Performance Optimization**
   - Efficient resource utilization
   - Caching of domain-specific pipelines
   - Monitoring of processing metrics
   - Dynamic scaling based on workload

4. **Error Handling**
   - Comprehensive error detection
   - Graceful degradation on component failures
   - Detailed error reporting
   - Recovery strategies for different error types

5. **Extensibility**
   - Plugin architecture for custom components
   - Support for different LLM providers
   - Domain-specific customizations
   - Integration with external systems

## Testing Strategy

### Unit Tests

1. **Component Integration Tests**
   - Test coordination between components
   - Verify correct data flow through pipeline
   - Test configuration application
   - Verify error handling

2. **Pipeline Factory Tests**
   - Test creation of pipelines with different configurations
   - Verify component initialization
   - Test configuration overrides
   - Verify pipeline caching

3. **Service Tests**
   - Test request handling
   - Verify domain-specific pipeline selection
   - Test error handling at service level
   - Verify result formatting

### Integration Tests

1. **End-to-End Pipeline Tests**
   - Test complete extraction process
   - Verify correct handling of different document types
   - Test with various field combinations
   - Measure end-to-end performance

2. **Domain-Specific Tests**
   - Test with medical records
   - Test with legal documents
   - Test with financial reports
   - Verify domain-specific configurations

### Performance Tests

1. **Throughput Tests**
   - Measure documents processed per minute
   - Test with varying document sizes
   - Verify scaling with concurrent requests
   - Measure resource utilization

2. **Latency Tests**
   - Measure end-to-end processing time
   - Test component-specific latencies
   - Verify performance with different configurations
   - Identify bottlenecks

## Example Usage

```python
import asyncio
from typing import Dict, Any

async def main():
    # Initialize services
    config_service = ConfigurationService("config/")
    logger = LoggingService()
    error_handler = ErrorHandlingService(logger)
    
    # Create pipeline factory
    pipeline_factory = PipelineFactory(
        config_service=config_service,
        logger=logger,
        error_handler=error_handler
    )
    
    # Create extraction service
    extraction_service = ExtractionService(
        pipeline_factory=pipeline_factory,
        config_service=config_service,
        logger=logger,
        error_handler=error_handler
    )
    
    # Sample document
    with open("sample_medical_record.txt", "r") as f:
        document = f.read()
    
    # Create extraction request
    request = ExtractionRequest(
        document=document,
        fields=["patient_name", "date_of_birth", "diagnoses", "medications"],
        domain="medical",
        output_formats=["json", "text"]
    )
    
    # Process request
    result = await extraction_service.extract(request)
    
    # Print results
    print(f"Extraction completed in {result.metadata['processing_time']:.2f} seconds")
    print(f"Processed {result.metadata['chunk_count']} chunks")
    print(f"Total tokens: {result.metadata['token_count']}")
    
    if result.json_output:
        print("\nJSON Output:")
        print(json.dumps(result.json_output, indent=2))
    
    if result.text_output:
        print("\nText Output:")
        print(result.text_output)
    
    # Check for warnings
    if result.metadata.get("warnings"):
        print("\nWarnings:")
        for warning in result.metadata["warnings"]:
            print(f"- {warning}")

# Run the async function
asyncio.run(main())
