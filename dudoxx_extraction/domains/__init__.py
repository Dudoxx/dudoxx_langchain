"""
Domain definitions for the Dudoxx Extraction system.

This package contains domain definitions for the extraction system, which define
the fields to extract for different domains and sub-domains.
"""

from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_init import initialize_domains

__all__ = [
    "DomainRegistry",
    "DomainDefinition",
    "SubDomainDefinition",
    "FieldDefinition",
    "initialize_domains"
]

# Initialize domains when this package is imported
initialize_domains()
