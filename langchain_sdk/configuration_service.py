"""
Configuration Service for Automated Large-Text Field Extraction Solution

This module provides a service for managing domain-specific configurations.
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional


class ConfigurationService:
    """Service for managing domain-specific configurations."""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize configuration service.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self.global_config = None
        self.domain_configs = {}
        
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(os.path.join(config_dir, "domains"), exist_ok=True)
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        """Load configurations from files."""
        # Load global configuration
        global_config_path = os.path.join(self.config_dir, "global.yaml")
        if os.path.exists(global_config_path):
            with open(global_config_path, "r") as f:
                self.global_config = yaml.safe_load(f)
        else:
            # Create default global configuration
            self.global_config = self._create_default_global_config()
            with open(global_config_path, "w") as f:
                yaml.dump(self.global_config, f, default_flow_style=False)
        
        # Load domain configurations
        domains_dir = os.path.join(self.config_dir, "domains")
        for filename in os.listdir(domains_dir):
            if filename.endswith(".yaml"):
                domain_path = os.path.join(domains_dir, filename)
                with open(domain_path, "r") as f:
                    domain_config = yaml.safe_load(f)
                    if domain_config and "name" in domain_config:
                        self.domain_configs[domain_config["name"]] = domain_config
        
        # Create default domain configurations if none exist
        if not self.domain_configs:
            self._create_default_domain_configs()
    
    def _create_default_global_config(self) -> Dict[str, Any]:
        """
        Create default global configuration.
        
        Returns:
            Default global configuration
        """
        return {
            "chunking": {
                "max_chunk_size": 16000,
                "overlap_size": 200
            },
            "extraction": {
                "model_name": "gpt-4",
                "temperature": 0.0
            },
            "processing": {
                "max_concurrency": 20
            },
            "merging": {
                "deduplication_threshold": 0.9
            }
        }
    
    def _create_default_domain_configs(self) -> None:
        """Create default domain configurations."""
        # Medical domain
        medical_config = {
            "name": "medical",
            "description": "Medical domain for healthcare documents",
            "fields": [
                {
                    "name": "patient_name",
                    "description": "Full name of the patient",
                    "type": "string",
                    "is_unique": True
                },
                {
                    "name": "date_of_birth",
                    "description": "Patient's date of birth",
                    "type": "date",
                    "is_unique": True
                },
                {
                    "name": "gender",
                    "description": "Patient's gender",
                    "type": "string",
                    "is_unique": True
                },
                {
                    "name": "medical_record_number",
                    "description": "Medical record number",
                    "type": "string",
                    "is_unique": True
                },
                {
                    "name": "allergies",
                    "description": "List of patient allergies",
                    "type": "list",
                    "is_unique": False
                },
                {
                    "name": "chronic_conditions",
                    "description": "List of chronic conditions",
                    "type": "list",
                    "is_unique": False
                },
                {
                    "name": "medications",
                    "description": "List of current medications",
                    "type": "list",
                    "is_unique": False
                },
                {
                    "name": "diagnoses",
                    "description": "List of diagnoses",
                    "type": "list",
                    "is_unique": False
                },
                {
                    "name": "visits",
                    "description": "List of medical visits with dates and descriptions",
                    "type": "list",
                    "is_unique": False
                }
            ]
        }
        
        # Legal domain
        legal_config = {
            "name": "legal",
            "description": "Legal domain for contracts and agreements",
            "fields": [
                {
                    "name": "title",
                    "description": "Title of the agreement",
                    "type": "string",
                    "is_unique": True
                },
                {
                    "name": "parties",
                    "description": "Parties involved in the agreement",
                    "type": "list",
                    "is_unique": False
                },
                {
                    "name": "effective_date",
                    "description": "Date when the agreement becomes effective",
                    "type": "date",
                    "is_unique": True
                },
                {
                    "name": "termination_date",
                    "description": "Date when the agreement terminates",
                    "type": "date",
                    "is_unique": True
                },
                {
                    "name": "obligations",
                    "description": "List of obligations for each party",
                    "type": "list",
                    "is_unique": False
                },
                {
                    "name": "governing_law",
                    "description": "Governing law for the agreement",
                    "type": "string",
                    "is_unique": True
                },
                {
                    "name": "events",
                    "description": "List of events with dates and descriptions",
                    "type": "list",
                    "is_unique": False
                }
            ]
        }
        
        # Save domain configurations
        domains_dir = os.path.join(self.config_dir, "domains")
        
        with open(os.path.join(domains_dir, "medical.yaml"), "w") as f:
            yaml.dump(medical_config, f, default_flow_style=False)
        
        with open(os.path.join(domains_dir, "legal.yaml"), "w") as f:
            yaml.dump(legal_config, f, default_flow_style=False)
        
        # Add to domain configs
        self.domain_configs["medical"] = medical_config
        self.domain_configs["legal"] = legal_config
    
    def get_global_config(self) -> Dict[str, Any]:
        """
        Get global configuration.
        
        Returns:
            Global configuration
        """
        return self.global_config
    
    def get_domains(self) -> List[Dict[str, Any]]:
        """
        Get available domains.
        
        Returns:
            List of domain information
        """
        domains = []
        for domain_name, domain_config in self.domain_configs.items():
            domains.append({
                "name": domain_name,
                "description": domain_config.get("description", ""),
                "fields": [field["name"] for field in domain_config.get("fields", [])]
            })
        
        return domains
    
    def get_domain_config(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get domain configuration.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain configuration or None if not found
        """
        return self.domain_configs.get(domain)
    
    def get_field_names(self, domain: str) -> List[str]:
        """
        Get field names for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of field names
        """
        domain_config = self.get_domain_config(domain)
        if not domain_config:
            return []
        
        return [field["name"] for field in domain_config.get("fields", [])]
    
    def get_field_descriptions(self, fields: List[str]) -> Dict[str, str]:
        """
        Get field descriptions for a list of fields.
        
        Args:
            fields: List of field names
            
        Returns:
            Dictionary of field descriptions
        """
        descriptions = {}
        
        for domain_config in self.domain_configs.values():
            for field_config in domain_config.get("fields", []):
                if field_config["name"] in fields:
                    descriptions[field_config["name"]] = field_config.get("description", "")
        
        return descriptions
    
    def get_domain_fields(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get fields for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of field information
        """
        domain_config = self.get_domain_config(domain)
        if not domain_config:
            return []
        
        return domain_config.get("fields", [])


def create_default_config(output_dir: str) -> None:
    """
    Create default configuration files.
    
    Args:
        output_dir: Output directory
    """
    # Create configuration service
    config_service = ConfigurationService(output_dir)
    
    # Get configurations
    global_config = config_service.get_global_config()
    domains = config_service.get_domains()
    
    print(f"Created global configuration in {output_dir}/global.yaml")
    print(f"Created domain configurations:")
    for domain in domains:
        print(f"- {domain['name']}: {domain['description']}")
