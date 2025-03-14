# Dudoxx LangChain SDK

This package provides a solution for extracting structured information from large text documents using LangChain components and Large Language Models (LLMs). This is part of the Dudoxx LangChain project maintained by the Dudoxx organization.

## Features

- **Document Chunking**: Intelligently splits large documents into manageable chunks
- **Parallel Processing**: Processes document chunks in parallel for faster extraction
- **Field Extraction**: Extracts structured fields from text using LLMs
- **Temporal Normalization**: Normalizes dates and constructs timelines
- **Result Merging & Deduplication**: Merges results from multiple chunks and deduplicates using embeddings
- **Output Formatting**: Generates structured outputs in JSON, text, and XML formats
- **Domain-Specific Configuration**: Supports different domains with configurable fields
- **API Service**: Provides a RESTful API for integration with other systems
- **Command-Line Interface**: Offers a CLI for easy usage
- **Environment Configuration**: Supports configuration via .env file

## Installation

```bash
# Install from source
git clone https://github.com/Dudoxx/dudoxx_langchain.git
cd dudoxx_langchain
pip install -e .

# Install from PyPI (once published)
pip install dudoxx-langchain
```

## Environment Configuration

The package supports configuration via a `.env` file. Create a `.env` file in the root directory of your project with the following variables:

```
OPENAI_BASE_URL=https://llm-proxy.dudoxx.com/v1
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=dudoxx
```

These settings will override any system environment variables with the same names.

## Quick Start

### Python API

```python
from dudoxx_extraction import ExtractionClientSync

# Initialize client (will automatically load settings from .env)
client = ExtractionClientSync()

# Extract from text
result = client.extract_text(
    text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
    fields=["patient_name", "date_of_birth", "diagnoses"],
    domain="medical"
)

# Access results
json_output = result["json_output"]
text_output = result["text_output"]
processing_time = result["metadata"]["processing_time"]
```

### Command Line

```bash
# Initialize configuration
dudoxx-extraction init-config

# List available domains
dudoxx-extraction list-domains

# Extract from file
dudoxx-extraction extract document.pdf --domain medical --fields patient_name date_of_birth diagnoses

# Start API server
dudoxx-extraction api
```

### REST API

```bash
# Extract from text
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
    "fields": ["patient_name", "date_of_birth", "diagnoses"],
    "domain": "medical"
  }'
```

## Using PydanticOutputParser

The package includes an example of using PydanticOutputParser for strongly typed extraction results:

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Get OpenAI settings from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# Try to import from langchain_openai (recommended)
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fall back to langchain_community if langchain_openai is not installed
    from langchain_community.chat_models import ChatOpenAI

# Define your Pydantic model
class MedicalRecord(BaseModel):
    patient_name: str = Field(description="Full name of the patient")
    date_of_birth: str = Field(description="Patient's date of birth")
    diagnoses: list[str] = Field(description="List of diagnoses")

# Set up parser
parser = PydanticOutputParser(pydantic_object=MedicalRecord)

# Initialize ChatOpenAI with settings from .env
llm = ChatOpenAI(
    model_name=openai_model_name,
    temperature=0,
    openai_api_key=openai_api_key,
    openai_api_base=openai_base_url
)

# Create prompt template
prompt = PromptTemplate(
    template="Extract the following information from the medical document.\n{format_instructions}\n\nDocument:\n{document}\n",
    input_variables=["document"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Create chain
chain = prompt | llm | parser

# Extract information
result = chain.invoke({"document": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II"})

# Access results (strongly typed)
print(f"Patient Name: {result.patient_name}")
print(f"Date of Birth: {result.date_of_birth}")
print(f"Diagnoses: {', '.join(result.diagnoses)}")
```

For a more comprehensive example, see `pydantic_parser_example.py`.

## Architecture

The extraction pipeline consists of the following components:

1. **Document Loaders**: Load documents from various sources (PDF, DOCX, text)
2. **Text Splitter**: Split documents into manageable chunks
3. **LLM**: Extract structured information from chunks
4. **Output Parser**: Parse LLM output into structured format
5. **Temporal Normalizer**: Normalize dates and construct timelines
6. **Result Merger**: Merge and deduplicate results from multiple chunks
7. **Output Formatter**: Format results in different formats (JSON, text, XML)

## Configuration

The extraction pipeline can be configured using YAML files in the configuration directory:

```yaml
# config/global.yaml
chunking:
  max_chunk_size: 16000
  overlap_size: 200

extraction:
  model_name: "gpt-4"
  temperature: 0.0

processing:
  max_concurrency: 20

merging:
  deduplication_threshold: 0.9
```

Domain-specific configurations can be defined in separate files:

```yaml
# config/domains/medical.yaml
name: medical
description: Medical domain for healthcare documents

fields:
  - name: patient_name
    description: Full name of the patient
    type: string
    is_unique: true
  
  - name: date_of_birth
    description: Patient's date of birth
    type: date
    is_unique: true
  
  - name: diagnoses
    description: List of diagnoses
    type: list
    is_unique: false
```

## API Reference

### ExtractionClient

```python
client = ExtractionClient(
    api_key=None,  # API key for authentication (for API mode)
    base_url=None,  # Base URL of the API service (for API mode)
    config_dir="./config",  # Configuration directory
    use_api=False  # Whether to use the API service
)
```

#### Methods

- `extract_text(text, fields, domain, output_formats=["json", "text"])`: Extract from text
- `extract_file(file_path, fields, domain, output_formats=["json", "text"])`: Extract from file
- `get_domains()`: Get available domains
- `get_domain_fields(domain)`: Get fields for a domain

### ExtractionClientSync

Synchronous version of ExtractionClient with the same methods.

## License

MIT
