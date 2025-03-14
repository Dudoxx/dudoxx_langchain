"""
Domain registry for the Dudoxx Extraction system.

This module provides a registry for domains, which allows for registering
and retrieving domain definitions.
"""

from typing import Dict, List, Optional
from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition


class DomainRegistry:
    """
    Registry for domain definitions.
    
    This class provides methods for registering and retrieving domain definitions.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a new instance of the domain registry.
        
        Returns:
            DomainRegistry: Domain registry instance
        """
        if cls._instance is None:
            cls._instance = super(DomainRegistry, cls).__new__(cls)
            cls._instance._domains = {}
            
        return cls._instance
    
    def register_domain(self, domain: DomainDefinition) -> None:
        """
        Register a domain definition.
        
        Args:
            domain: Domain definition to register
        """
        self._domains[domain.name] = domain
    
    def get_domain(self, name: str) -> Optional[DomainDefinition]:
        """
        Get a domain definition by name.
        
        Args:
            name: Name of the domain
            
        Returns:
            Optional[DomainDefinition]: Domain definition or None if not found
        """
        return self._domains.get(name)
    
    def get_all_domains(self) -> List[DomainDefinition]:
        """
        Get all registered domain definitions.
        
        Returns:
            List[DomainDefinition]: List of domain definitions
        """
        return list(self._domains.values())
    
    def get_domain_names(self) -> List[str]:
        """
        Get the names of all registered domains.
        
        Returns:
            List[str]: List of domain names
        """
        return list(self._domains.keys())
    
    def get_sub_domain(self, domain_name: str, sub_domain_name: str) -> Optional[SubDomainDefinition]:
        """
        Get a sub-domain definition by domain name and sub-domain name.
        
        Args:
            domain_name: Name of the domain
            sub_domain_name: Name of the sub-domain
            
        Returns:
            Optional[SubDomainDefinition]: Sub-domain definition or None if not found
        """
        domain = self.get_domain(domain_name)
        
        if domain is None:
            return None
            
        return domain.get_sub_domain(sub_domain_name)
