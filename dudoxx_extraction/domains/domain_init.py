"""
Domain initialization for the Dudoxx Extraction system.

This module initializes and registers all domain definitions.
"""

from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.domains.medical_domain import register_medical_domain
from dudoxx_extraction.domains.legal_domain import register_legal_domain


def initialize_domains():
    """
    Initialize and register all domain definitions.
    
    This function should be called at application startup to ensure
    all domains are registered with the domain registry.
    """
    # Register medical domain
    register_medical_domain()
    
    # Register legal domain
    register_legal_domain()
    
    # Log registered domains
    registry = DomainRegistry()
    domain_names = registry.get_domain_names()
    print(f"Registered domains: {', '.join(domain_names)}")


# Initialize domains when this module is imported
initialize_domains()
