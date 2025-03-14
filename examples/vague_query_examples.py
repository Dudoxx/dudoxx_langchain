"""
Examples of using the Domain Identifier with vague extraction requests.

This script demonstrates how the Domain Identifier handles different types of
vague queries and provides focused extraction schemas.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dudoxx_extraction.domain_identifier import DomainIdentifier


def run_query_examples():
    """Run examples of vague queries through the Domain Identifier."""
    # Create domain identifier
    domain_identifier = DomainIdentifier(use_rich_logging=True)
    
    # List of vague queries to test
    vague_queries = [
        "What are the patient information?",
        "Extract all important dates",
        "Get contact details",
        "Find all names in the document",
        "What are the legal terms?",
        "Extract payment information",
        "Get all medical history",
        "Find identification numbers"
    ]
    
    # Process each query
    for query in vague_queries:
        print("\n" + "="*80)
        print(f"QUERY: {query}")
        print("="*80)
        
        # Get extraction schema
        extraction_schema = domain_identifier.get_extraction_schema(query)
        
        # Print a summary of the results
        print("\nSUMMARY:")
        domains_included = list(extraction_schema.keys())
        field_count = sum(len(fields) for subdomain in extraction_schema.values() 
                          for fields in subdomain.values())
        
        print(f"- Domains included: {', '.join(domains_included)}")
        print(f"- Total fields selected: {field_count}")
        
        # Print the top field for each domain
        print("\nTOP FIELDS BY DOMAIN:")
        for domain, subdomains in extraction_schema.items():
            for subdomain, fields in subdomains.items():
                if fields:
                    # Sort fields by confidence
                    sorted_fields = sorted(fields, key=lambda x: x[1], reverse=True)
                    top_field, confidence = sorted_fields[0]
                    print(f"- {domain}.{subdomain}.{top_field} (confidence: {confidence:.2f})")


if __name__ == "__main__":
    run_query_examples()
