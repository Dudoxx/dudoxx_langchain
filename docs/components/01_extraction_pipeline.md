# Extraction Pipeline

The `ExtractionPipeline` is the core component of the Dudoxx Extraction system. It orchestrates the entire extraction process, from loading documents to formatting the final output.

## Overview

The extraction pipeline follows a modular design pattern, where each step in the process is handled by a specialized component. This design allows for easy customization and extension of the pipeline.

## Key Components

The pipeline integrates several key components:

1. **Document Loader**: Loads documents from various sources (text files, PDFs, etc.)
2. **Text Splitter**: Splits large documents into manageable chunks
3. **LLM (Language Model)**: Processes text chunks to extract information
4. **Output Parser**: Parses the LLM output into structured data
5. **Temporal Normalizer**: Normalizes dates and constructs timelines
6. **Result Merger**: Merges and deduplicates results from multiple chunks
7. **Output Formatter**: Formats the final output in various formats (JSON, text, XML)

## Implementation

The `ExtractionPipeline` class is implemented in `langchain_sdk/extraction_pipeline.py` and `dudoxx_extraction/extraction_pipeline.py`. Here's a simplified version of the class:

```python
class ExtractionPipeline:
    def __init__(self, 
                 document_loader,
                 text_splitter,
                 llm,
                 output_parser,
                 temporal_normalizer=None,
                 result_merger=None,
                 output_formatter=None,
                 max_concurrency=20,
                 logger=None):
        # Initialize components
        self.document_loader = document_loader
        self.text_splitter = text_splitter
        self.llm = llm
        self.output_parser = output_parser
        self.temporal_normalizer = temporal_normalizer or TemporalNormalizer(llm, logger)
        self.result_merger = result_merger or ResultMerger(logger=logger)
        self.output_formatter = output_formatter or OutputFormatter(logger)
        self.max_concurrency = max_concurrency
        self.logger = logger
        
    async def process_document(self, document_path, fields, domain, output_formats=["json", "text"]):
        # Step 1: Load document
        loader = self.document_loader(document_path)
        documents = loader.load()
        
        # Step 2: Split document into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Step 3: Process chunks in parallel
        chunk_results = await self._process_chunks(chunks, fields, domain)
        
        # Step 4: Normalize temporal data
        normalized_results = self._normalize_temporal_data(chunk_results)
        
        # Step 5: Merge and deduplicate results
        merged_result = self.result_merger.merge_results(normalized_results)
        
        # Step 6: Format output
        output = self._format_output(merged_result, output_formats)
        
        return output
```

## Process Flow

1. **Document Loading**: The pipeline loads the document using the specified document loader.
2. **Document Chunking**: Large documents are split into manageable chunks using the text splitter.
3. **Parallel Processing**: Each chunk is processed in parallel using the LLM and output parser.
4. **Temporal Normalization**: Dates and timelines are normalized for consistency.
5. **Result Merging**: Results from multiple chunks are merged and deduplicated.
6. **Output Formatting**: The final result is formatted in the requested output formats.

## Concurrency Control

The pipeline uses asyncio for concurrent processing of document chunks, with a semaphore to limit the number of concurrent LLM requests:

```python
async def _process_chunks(self, chunks, fields, domain):
    semaphore = asyncio.Semaphore(self.max_concurrency)
    
    async def process_chunk(chunk_index, chunk):
        async with semaphore:
            # Process chunk with LLM
            # ...
    
    # Create tasks for all chunks
    tasks = [process_chunk(i, chunk) for i, chunk in enumerate(chunks)]
    
    # Execute tasks in parallel
    return await asyncio.gather(*tasks)
```

## Error Handling

The pipeline includes robust error handling at each step:

1. **LLM Processing Errors**: If the LLM fails to process a chunk, the pipeline returns an empty result for that chunk.
2. **Parsing Errors**: If the output parser fails to parse the LLM output, the pipeline returns an empty result for that chunk.
3. **Logging**: All errors are logged with detailed information for debugging.

## Usage Example

```python
# Initialize components
document_loader = TextLoader
text_splitter = RecursiveCharacterTextSplitter(chunk_size=16000, chunk_overlap=200)
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
output_parser = PydanticOutputParser(pydantic_object=ExtractionModel)

# Create pipeline
pipeline = ExtractionPipeline(
    document_loader=document_loader,
    text_splitter=text_splitter,
    llm=llm,
    output_parser=output_parser
)

# Process document
result = await pipeline.process_document(
    document_path="examples/medical_record.txt",
    fields=["patient_name", "date_of_birth", "diagnoses", "medications", "visits"],
    domain="medical",
    output_formats=["json", "text", "xml"]
)
```

## Customization

The pipeline is designed to be highly customizable. You can provide your own implementations of any component:

- **Document Loader**: Use different loaders for different document types
- **Text Splitter**: Customize the chunking strategy
- **LLM**: Use different language models or providers
- **Output Parser**: Define custom parsing logic
- **Temporal Normalizer**: Implement custom date normalization
- **Result Merger**: Customize the merging and deduplication logic
- **Output Formatter**: Define custom output formats
