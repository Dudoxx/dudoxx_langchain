# Dudoxx LangChain

A robust, scalable solution for extracting structured information from large text documents using LangChain components and LLM technology. This repository is maintained by the Dudoxx organization.

## Features

- **Flexible Document Processing**: Support for various document formats (TXT, PDF) with automatic chunking for large documents
- **Parallel Processing**: Concurrent processing of document chunks for faster extraction
- **Domain-Based Extraction**: Structured domain definitions with sub-domains for focused extraction
- **Parallel Sub-Domain Processing**: Process multiple sub-domains in parallel for each document chunk
- **Temporal Data Normalization**: Automatic normalization of dates and construction of timelines
- **Result Merging and Deduplication**: Smart merging of results from multiple chunks with deduplication
- **Multiple Output Formats**: JSON, text, and XML output formats
- **Rich Logging**: Beautiful console UI with detailed step-by-step logging
- **Customizable Fields**: Extract specific fields based on your needs
- **Domain-Specific Extraction**: Support for medical, legal, and other domains
- **Environment Configuration**: Easy configuration via `.env` file

## Architecture

The solution consists of several components:

1. **ExtractionPipeline**: The main pipeline that orchestrates the extraction process
2. **ParallelExtractionPipeline**: Advanced pipeline that processes multiple sub-domains in parallel
3. **Domain Registry**: Registry for domain definitions with sub-domains and fields
4. **TemporalNormalizer**: Handles date normalization and timeline construction
5. **ResultMerger**: Merges and deduplicates results from multiple chunks
6. **OutputFormatter**: Formats extraction results in different formats
7. **RichLogger**: Provides rich console output with syntax highlighting
8. **Client Interface**: Both synchronous and asynchronous clients for easy integration

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:

```bash
git clone https://github.com/Dudoxx/dudoxx_langchain.git
cd dudoxx_langchain
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_BASE_URL=https://llm-proxy.dudoxx.com/v1
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=dudoxx
OPENAI_EMBEDDING_MODEL=embedder
```

## Usage

### Basic Usage

```python
from dudoxx_extraction.client import ExtractionClientSync

# Initialize client
client = ExtractionClientSync()

# Extract from text
result = client.extract_text(
    text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes",
    fields=["patient_name", "date_of_birth", "diagnoses"],
    domain="medical"
)

# Print results
print(f"JSON output: {result['json_output']}")
print(f"Text output: {result['text_output']}")
```

### File Extraction

```python
# Extract from file
result = client.extract_file(
    file_path="examples/medical_record.txt",
    fields=["patient_name", "date_of_birth", "diagnoses", "medications", "visits"],
    domain="medical"
)
```

### Running the Examples

The repository includes example scripts that demonstrate the extraction capabilities:

```bash
# Run the basic example script
python dudoxx_extraction_example.py

# Run the standalone example
python standalone_example.py

# Run the parallel extraction example
python examples/parallel_extraction_example.py
```

## Project Structure

```
dudoxx_langchain/
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── requirements.txt          # Project dependencies
├── dudoxx_extraction/        # Main package
│   ├── __init__.py           # Package initialization
│   ├── client.py             # Client interface
│   ├── example.py            # Example usage
│   ├── extraction_pipeline.py # Main extraction pipeline
│   └── README.md             # Package documentation
├── langchain_sdk/            # LangChain SDK
│   ├── __init__.py           # Package initialization
│   ├── api_service.py        # API service
│   ├── client.py             # Client interface
│   ├── configuration_service.py # Configuration service
│   ├── example.py            # Example usage
│   ├── extraction_pipeline.py # Extraction pipeline
│   ├── logger.py             # Rich logger
│   ├── pydantic_parser_example.py # Pydantic parser example
│   ├── README.md             # Package documentation
│   └── setup.py              # Package setup
├── examples/                 # Example documents
│   ├── medical_record.txt    # Example medical record
│   └── legal_agreement.txt   # Example legal agreement
└── standalone_example.py     # Standalone example
```

## Configuration

The solution uses environment variables for configuration, which can be loaded from a `.env` file:

```
OPENAI_BASE_URL=https://llm-proxy.dudoxx.com/v1
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=dudoxx
OPENAI_EMBEDDING_MODEL=embedder
```

## Advanced Usage

### Using the Parallel Extraction Pipeline

The parallel extraction pipeline allows you to process multiple sub-domains in parallel for each document chunk:

```python
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync

# Extract from file with all sub-domains
result = extract_document_sync(
    document_path="examples/medical_record.txt",
    domain_name="medical",
    output_formats=["json", "text"]
)

# Extract from file with specific sub-domains
result = extract_document_sync(
    document_path="examples/medical_record.txt",
    domain_name="medical",
    sub_domain_names=["patient_info", "medications", "diagnoses"],
    output_formats=["json", "text"]
)
```

### Creating Custom Domains

You can create custom domains with sub-domains for focused extraction:

```python
from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry

# Create a sub-domain
custom_subdomain = SubDomainDefinition(
    name="custom_subdomain",
    description="custom information",
    fields=[
        FieldDefinition(
            name="field1",
            description="Description of field1",
            type="string",
            is_required=True
        ),
        FieldDefinition(
            name="field2",
            description="Description of field2",
            type="list",
            is_required=False
        )
    ]
)

# Create a domain with the sub-domain
custom_domain = DomainDefinition(
    name="custom_domain",
    description="Custom domain for specific documents",
    sub_domains=[custom_subdomain]
)

# Register the domain
registry = DomainRegistry()
registry.register_domain(custom_domain)

# Use the domain with the parallel extraction pipeline
result = extract_document_sync(
    document_path="path/to/document.txt",
    domain_name="custom_domain",
    output_formats=["json", "text"]
)
```

### Customizing the Pipeline

You can customize the extraction pipeline by providing your own components:

```python
from dudoxx_extraction.extraction_pipeline import ExtractionPipeline
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# Define your own extraction model
class CustomExtractionModel(BaseModel):
    title: str = Field(description="Document title")
    author: str = Field(description="Document author")
    keywords: Optional[List[str]] = Field(description="Document keywords")

# Create custom components
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=8000,
    chunk_overlap=100
)

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0
)

output_parser = PydanticOutputParser(pydantic_object=CustomExtractionModel)

# Create pipeline
pipeline = ExtractionPipeline(
    document_loader=TextLoader,
    text_splitter=text_splitter,
    llm=llm,
    output_parser=output_parser
)

# Process document
result = await pipeline.process_document(
    document_path="path/to/document.txt",
    fields=["title", "author", "keywords"],
    domain="academic"
)
```

### Asynchronous API

The solution also provides an asynchronous API for use in async applications:

```python
from dudoxx_extraction.client import ExtractionClientAsync
import asyncio

async def extract_async():
    # Initialize client
    client = ExtractionClientAsync()
    
    # Extract from text
    result = await client.extract_text(
        text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes",
        fields=["patient_name", "date_of_birth", "diagnoses"],
        domain="medical"
    )
    
    # Print results
    print(f"JSON output: {result['json_output']}")

# Run async function
asyncio.run(extract_async())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
