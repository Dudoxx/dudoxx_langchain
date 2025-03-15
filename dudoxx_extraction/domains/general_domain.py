"""
General domain definitions for the Dudoxx Extraction system.

This module provides a general-purpose domain definition for extracting
information from text when no specific domain is identified.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# General Content Sub-Domain
general_content_subdomain = SubDomainDefinition(
    name="general_content",
    description="general content information",
    fields=[
        FieldDefinition(
            name="content",
            description="General content extracted from the text",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["This is some general content extracted from the text."]
        ),
        FieldDefinition(
            name="entities",
            description="Named entities found in the text (people, organizations, locations, etc.)",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"type": "PERSON", "text": "John Smith", "position": [10, 20]},
                {"type": "ORGANIZATION", "text": "Acme Corporation", "position": [45, 60]},
                {"type": "LOCATION", "text": "San Francisco", "position": [75, 88]}
            ]
        ),
        FieldDefinition(
            name="dates",
            description="Dates mentioned in the text",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"date": "2023-05-15", "original_text": "May 15, 2023", "position": [100, 112]},
                {"date": "2022-12-25", "original_text": "Christmas 2022", "position": [150, 165]}
            ]
        ),
        FieldDefinition(
            name="numbers",
            description="Numerical values found in the text",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"value": 42, "original_text": "42", "position": [200, 202]},
                {"value": 3.14, "original_text": "3.14", "position": [220, 224]},
                {"value": 1000000, "original_text": "1 million", "position": [240, 249]}
            ]
        )
    ]
)

# Key-Value Pairs Sub-Domain
key_value_subdomain = SubDomainDefinition(
    name="key_value_pairs",
    description="key-value pairs extracted from the text",
    fields=[
        FieldDefinition(
            name="pairs",
            description="Key-value pairs extracted from the text",
            type="list",
            is_required=True,
            is_unique=False,
            examples=[
                {"key": "Name", "value": "John Smith"},
                {"key": "Email", "value": "john.smith@example.com"},
                {"key": "Phone", "value": "+1 (555) 123-4567"}
            ]
        )
    ]
)

# Summary Sub-Domain
summary_subdomain = SubDomainDefinition(
    name="summary",
    description="summary information",
    fields=[
        FieldDefinition(
            name="summary",
            description="Summary of the text content",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["This text discusses the benefits of renewable energy sources and their impact on climate change."]
        ),
        FieldDefinition(
            name="topics",
            description="Main topics discussed in the text",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Renewable Energy",
                "Climate Change",
                "Sustainability",
                "Environmental Policy"
            ]
        ),
        FieldDefinition(
            name="sentiment",
            description="Overall sentiment of the text",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "polarity": "positive",
                    "confidence": 0.85,
                    "explanation": "The text contains predominantly positive language about renewable energy solutions."
                }
            ]
        )
    ]
)

# Create the General Domain
general_domain = DomainDefinition(
    name="general",
    description="General-purpose domain for extracting information when no specific domain is identified",
    sub_domains=[
        general_content_subdomain,
        key_value_subdomain,
        summary_subdomain
    ]
)

# Register the domain
def register_general_domain():
    """Register the general domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(general_domain)
