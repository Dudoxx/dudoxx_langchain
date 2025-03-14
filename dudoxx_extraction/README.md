# Dudoxx Extraction

A powerful, domain-aware extraction framework for extracting structured information from unstructured text documents.

## Overview

Dudoxx Extraction is a comprehensive framework that combines domain knowledge with advanced LLM capabilities to extract structured information from various document types. The framework is designed to be flexible, extensible, and easy to use, making it suitable for a wide range of extraction tasks across different domains.

## Key Components

### Domain Identifier

- Custom LLM endpoint support

## Installation

```bash
# Clone the repository
git clone https://github.com/Dudoxx/dudoxx_langchain.git

# Install dependencies
cd dudoxx_langchain
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in your project directory with the following settings:

```
OPENAI_BASE_URL=https://llm-proxy.dudoxx.com/v1
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=dudoxx
```

If you don't create a `.env` file, the package will use the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_BASE_URL`: The base URL for the OpenAI API (optional)
- `OPENAI_MODEL_NAME`: The model name to use (defaults to "gpt-4o-mini")

## Usage

### Basic Usage

```python
from dudoxx_extraction.client import ExtractionClientSync

# Initialize client
client = ExtractionClientSync()

# Extract from text
result = client.extract_text(
    text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
    fields=["patient_name", "date_of_birth", "diagnoses"],
    domain="medical"
)

# Print results
print(f"JSON output: {result['json_output']}")
print(f"Text output: {result['text_output']}")
```

### Extracting from a File

```python
from dudoxx_extraction.client import ExtractionClientSync

# Initialize client
client = ExtractionClientSync()

# Extract from file
result = client.extract_file(
    file_path="medical_record.txt",
    fields=["patient_name", "date_of_birth", "diagnoses", "medications", "visits"],
    domain="medical"
)

# Print results
print(f"JSON output: {result['json_output']}")
print(f"Text output: {result['text_output']}")
```

### Asynchronous API

```python
import asyncio
from dudoxx_extraction.client import ExtractionClient

async def extract_async():
    # Initialize client
    client = ExtractionClient()
    
    # Extract from text
    result = await client.extract_text(
        text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
        fields=["patient_name", "date_of_birth", "diagnoses"],
        domain="medical"
    )
    
    # Print results
    print(f"JSON output: {result['json_output']}")
    print(f"Text output: {result['text_output']}")

# Run async function
asyncio.run(extract_async())
```

### Direct Access to Extraction Functions

```python
from dudoxx_extraction.extraction_pipeline import extract_text, extract_file

# Extract from text
result = extract_text(
    text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
    fields=["patient_name", "date_of_birth", "diagnoses"],
    domain="medical"
)

# Print results
print(f"JSON output: {result['json_output']}")
print(f"Text output: {result['text_output']}")
```

## Supported Domains and Fields

### Medical Domain

- `patient_name`: Full name of the patient
- `date_of_birth`: Patient's date of birth
- `gender`: Patient's gender
- `medical_record_number`: Medical record number
- `allergies`: List of patient allergies
- `chronic_conditions`: List of chronic conditions
- `medications`: List of current medications
- `diagnoses`: List of diagnoses
- `visits`: List of medical visits with dates and descriptions

### Legal Domain

- `title`: Title of the agreement
- `parties`: Parties involved in the agreement
- `effective_date`: Date when the agreement becomes effective
- `termination_date`: Date when the agreement terminates
- `obligations`: List of obligations for each party
- `governing_law`: Governing law for the agreement
- `events`: List of events with dates and descriptions

## Advanced Usage

### Using with Pydantic Models

For strongly typed extraction results, you can use the `PydanticOutputParser` from LangChain:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Define Pydantic model
class MedicalRecord(BaseModel):
    patient_name: str = Field(description="Full name of the patient")
    date_of_birth: str = Field(description="Patient's date of birth")
    diagnoses: Optional[List[str]] = Field(description="List of diagnoses")

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Set up parser
parser = PydanticOutputParser(pydantic_object=MedicalRecord)

# Create prompt template
prompt = PromptTemplate(
    template="Extract the following information from the document.\n{format_instructions}\n\nDocument:\n{document}\n",
    input_variables=["document"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Create chain
chain = prompt | llm | parser

# Extract information
result = chain.invoke({"document": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II"})

# Print result
print(f"Patient Name: {result.patient_name}")
print(f"Date of Birth: {result.date_of_birth}")
print(f"Diagnoses: {result.diagnoses}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
