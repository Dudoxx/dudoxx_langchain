# Dudoxx Extraction

A powerful, domain-aware extraction framework for extracting structured information from unstructured text documents.

## Overview

Dudoxx Extraction is a comprehensive framework that combines domain knowledge with advanced LLM capabilities to extract structured information from various document types. The framework is designed to be flexible, extensible, and easy to use, making it suitable for a wide range of extraction tasks across different domains.

## Key Components

### Domain Identifier

The Domain Identifier is a core component that analyzes user queries to identify the most relevant domains and fields for extraction. It uses semantic matching and context-aware filtering to provide focused extraction schemas.

```python
from dudoxx_extraction.domain_identifier import DomainIdentifier

# Initialize domain identifier
domain_identifier = DomainIdentifier()

# Get extraction schema for a query
query = "What are the patient information?"
extraction_schema = domain_identifier.get_extraction_schema(query)

# The extraction schema contains the most relevant domains and fields for the query
print(extraction_schema)
```

### Extraction Pipeline

The Extraction Pipeline processes documents to extract structured information based on specified fields and domains. It handles document loading, chunking, extraction, and result merging.

```python
from dudoxx_extraction.extraction_pipeline import extract_file

# Extract information from a file
result = extract_file(
    file_path="data/legal_contract.txt",
    fields=["parties", "effective_date", "termination_provisions"],
    domain="legal",
    output_formats=["json", "text"]
)

# The result contains the extracted information in the specified formats
print(result["json_output"])
print(result["text_output"])
```

### Domain Registry

The Domain Registry manages domain definitions, which specify the structure and semantics of different domains. It provides a centralized repository for domain knowledge.

```python
from dudoxx_extraction.domains.domain_registry import DomainRegistry

# Get the domain registry singleton
registry = DomainRegistry()

# Get all available domains
domains = registry.get_all_domains()

# Get a specific domain
legal_domain = registry.get_domain("legal")

# Access domain information
print(legal_domain.name)
print(legal_domain.description)
print([sub.name for sub in legal_domain.sub_domains])
```

### Document Loaders

Document Loaders handle loading and preprocessing different document types, such as text, PDF, DOCX, HTML, and CSV files.

```python
from dudoxx_extraction.document_loaders.document_loader_factory import DocumentLoaderFactory

# Create a document loader for a specific file type
loader_factory = DocumentLoaderFactory()
loader = loader_factory.create_loader("data/document.pdf")

# Load the document
documents = loader.load()
```

## Domain-Based Extraction

The framework supports domain-based extraction, which combines the Domain Identifier and Extraction Pipeline to automatically extract relevant information based on natural language queries.

```python
from dudoxx_extraction.domain_identifier import DomainIdentifier
from dudoxx_extraction.extraction_pipeline import extract_file

# Initialize domain identifier
domain_identifier = DomainIdentifier()

# Get domain and fields for a query
query = "Extract all parties involved in the contract"
extraction_schema = domain_identifier.get_extraction_schema(query)

# Get the primary domain and fields
primary_domain = next(iter(extraction_schema.keys()))
fields = []
for subdomain, field_list in extraction_schema[primary_domain].items():
    for field_name, confidence in field_list:
        fields.append(field_name)

# Extract data using the identified domain and fields
result = extract_file(
    file_path="data/legal_contract.txt",
    fields=fields,
    domain=primary_domain,
    output_formats=["json", "text"]
)

# The result contains the extracted information
print(result["json_output"])
```

## Examples

The framework includes several examples that demonstrate its capabilities:

- `examples/domain_based_extraction.py`: Demonstrates domain-based extraction using natural language queries
- `examples/vague_query_examples.py`: Shows how the Domain Identifier handles vague extraction requests
- `examples/legal_document_example.py`: Extracts information from legal documents
- `examples/specialized_medical_example.py`: Extracts information from medical records
- `examples/parallel_extraction_example.py`: Demonstrates parallel extraction for improved performance

## Configuration

The framework can be configured using environment variables or a configuration file. See `docs/environment_configuration.md` for details.

## Contributing

Contributions are welcome! See `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
