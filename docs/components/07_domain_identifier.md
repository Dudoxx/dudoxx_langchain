# Domain Identifier

The Domain Identifier is a key component of the Dudoxx Extraction framework that analyzes user queries to identify the most relevant domains and fields for extraction. It uses semantic matching and context-aware filtering to provide focused extraction schemas.

## Overview

When users provide natural language queries for information extraction, they often don't know the exact domain structure or field names. The Domain Identifier bridges this gap by:

1. Analyzing the query semantics
2. Matching it against available domains and fields
3. Providing a focused extraction schema with the most relevant domains and fields

This enables a more intuitive and user-friendly extraction experience, where users can ask for information in natural language without needing to know the underlying domain structure.

## Key Features

- **Semantic Matching**: Uses advanced semantic matching to understand the intent of user queries
- **Context-Aware Filtering**: Filters domains and fields based on their relevance to the query
- **Confidence Scoring**: Provides confidence scores for each domain and field match
- **Multi-Word Keyword Detection**: Gives higher weight to multi-word keyword matches
- **Focused Results**: Returns only the most relevant domains and fields to prevent information overload

## Usage

### Basic Usage

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

### Integration with Extraction Pipeline

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

## Configuration

The Domain Identifier can be configured with the following parameters:

- **llm**: LangChain LLM to use for domain identification (default: uses ConfigurationService)
- **domain_registry**: Domain registry to use (default: uses singleton instance)
- **use_rich_logging**: Whether to use rich logging (default: True)

```python
from dudoxx_extraction.domain_identifier import DomainIdentifier
from langchain_openai import ChatOpenAI

# Create a custom LLM
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.0
)

# Initialize domain identifier with custom LLM
domain_identifier = DomainIdentifier(
    llm=llm,
    use_rich_logging=True
)
```

## Advanced Features

### Identifying Domains for a Query

The `identify_domains_for_query` method provides detailed information about domain matches:

```python
# Get detailed domain identification results
result = domain_identifier.identify_domains_for_query("What are the patient information?")

# Access matched domains
for domain_match in result.matched_domains:
    print(f"Domain: {domain_match.domain_name}, Confidence: {domain_match.confidence}")
    print(f"Reason: {domain_match.reason}")

# Access matched fields
for field_match in result.matched_fields:
    print(f"Field: {field_match.domain_name}.{field_match.sub_domain_name}.{field_match.field_name}")
    print(f"Confidence: {field_match.confidence}")
    print(f"Reason: {field_match.reason}")
```

### Handling Vague Queries

The Domain Identifier is designed to handle vague queries by focusing on the most relevant domains and fields:

```python
# Examples of vague queries
vague_queries = [
    "Extract all important dates",
    "Get contact details",
    "Find all names in the document",
    "What are the legal terms?",
    "Extract payment information"
]

# Process each query
for query in vague_queries:
    extraction_schema = domain_identifier.get_extraction_schema(query)
    print(f"Query: {query}")
    print(f"Domains: {list(extraction_schema.keys())}")
    print("Fields:")
    for domain, subdomains in extraction_schema.items():
        for subdomain, fields in subdomains.items():
            for field, confidence in fields:
                print(f"  - {domain}.{subdomain}.{field} ({confidence:.2f})")
    print()
```

## Implementation Details

The Domain Identifier uses a combination of techniques to match domains and fields to queries:

1. **Keyword Matching**: Matches keywords from the query against domain and field names and descriptions
2. **Semantic Relevance**: Calculates semantic relevance based on term overlap between the query and domain/field descriptions
3. **Confidence Scoring**: Assigns confidence scores based on the quality and quantity of matches
4. **Context-Aware Filtering**: Filters domains and fields based on their relevance to the query context

The implementation is designed to be generic and domain-agnostic, working with any domain structure defined in the Domain Registry.

## Best Practices

- **Use Clear Queries**: While the Domain Identifier can handle vague queries, clearer queries will generally yield better results
- **Review Extraction Schemas**: For critical applications, review the extraction schema before using it for extraction
- **Provide Domain Feedback**: If the Domain Identifier consistently misidentifies domains for certain queries, consider updating the domain descriptions or adding more specific keywords
