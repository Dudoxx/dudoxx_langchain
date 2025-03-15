"""
Prompt Builder for the Dudoxx Extraction system.

This module provides a class for building extraction prompts based on domain
and field definitions, with improved context and instructions.
"""

from typing import List, Dict, Any, Optional, Union
from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition


class PromptBuilder:
    """
    Builds extraction prompts based on enhanced domain and field definitions.
    
    This class generates comprehensive prompts for LLMs to extract information
    from documents, leveraging the rich metadata in domain definitions.
    """
    
    def __init__(self, domain_registry=None):
        """
        Initialize with domain registry.
        
        Args:
            domain_registry: Domain registry (if None, the singleton instance will be used)
        """
        self.domain_registry = domain_registry or DomainRegistry()
    
    def build_extraction_prompt(
        self, 
        text: str, 
        domain_name: str, 
        field_names: List[str] = None,
        sub_domain_names: List[str] = None
    ) -> str:
        """
        Build a comprehensive extraction prompt.
        
        Args:
            text: Text to extract from
            domain_name: Domain name
            field_names: Specific field names to extract (if None, use all fields from sub_domains)
            sub_domain_names: Sub-domain names to include (if None, use all sub-domains)
            
        Returns:
            Complete extraction prompt
        """
        # Get domain definition
        domain = self.domain_registry.get_domain(domain_name)
        if not domain:
            raise ValueError(f"Domain '{domain_name}' not found in registry")
            
        # Determine sub-domains to include
        if sub_domain_names:
            sub_domains = [domain.get_sub_domain(name) for name in sub_domain_names if domain.get_sub_domain(name)]
        else:
            sub_domains = domain.sub_domains
            
        if not sub_domains:
            raise ValueError(f"No valid sub-domains found for domain '{domain_name}'")
            
        # Build the prompt header with domain context
        prompt = self._build_prompt_header(domain)
        
        # Add domain-level extraction instructions if available
        if domain.extraction_instructions:
            prompt += f"\n{domain.extraction_instructions}\n"
        
        # Add field sections for each sub-domain
        for sub_domain in sub_domains:
            # Filter fields if specific field names were provided
            if field_names:
                fields = [f for f in sub_domain.fields if f.name in field_names]
            else:
                fields = sub_domain.fields
                
            if fields:
                prompt += self._build_subdomain_section(sub_domain, fields)
        
        # Add anti-hallucination instructions
        prompt += self._build_anti_hallucination_instructions()
        
        # Add formatting instructions
        prompt += self._build_formatting_instructions()
        
        # Add the text to extract from
        prompt += f"\nText:\n{text}\n"
        
        return prompt
    
    def _build_prompt_header(self, domain: DomainDefinition) -> str:
        """
        Build the prompt header with domain context.
        
        Args:
            domain: Domain definition
            
        Returns:
            Prompt header
        """
        return f"""# Extraction Task for {domain.name.title()} Domain

You are tasked with extracting specific information from the following {domain.name} document.
Domain description: {domain.description}

"""
    
    def _build_subdomain_section(self, sub_domain: SubDomainDefinition, fields: List[FieldDefinition]) -> str:
        """
        Build a section for a sub-domain with its fields.
        
        Args:
            sub_domain: Sub-domain definition
            fields: List of fields to include
            
        Returns:
            Sub-domain section
        """
        section = f"\n## {sub_domain.name.replace('_', ' ').title()}: {sub_domain.description}\n\n"
        
        # Add sub-domain extraction instructions if available
        if sub_domain.extraction_instructions:
            section += f"{sub_domain.extraction_instructions}\n\n"
            
        section += "Extract the following fields:\n\n"
        
        # Sort fields by priority if available
        sorted_fields = sorted(
            fields, 
            key=lambda f: (f.extraction_priority or 0), 
            reverse=True
        )
        
        for field in sorted_fields:
            section += field.to_prompt_text() + "\n"
            
        return section
    
    def _build_anti_hallucination_instructions(self) -> str:
        """
        Build instructions to prevent hallucination.
        
        Returns:
            Anti-hallucination instructions
        """
        return """
## Important: Anti-Hallucination Instructions

1. ONLY extract information that is EXPLICITLY stated in the text.
2. If a field is not found in the text, return null for that field.
3. DO NOT infer, assume, or generate information that is not directly present in the text.
4. If you're uncertain about a value, return null rather than guessing.
5. For list-type fields, only include items that are clearly mentioned in the text.
6. Do not extract information from section headers or metadata unless it's part of the actual content.
7. If multiple conflicting values are found for a field, extract the most specific or recent one.
"""
    
    def _build_formatting_instructions(self) -> str:
        """
        Build instructions for output formatting.
        
        Returns:
            Formatting instructions
        """
        return """
## Output Format Instructions

1. Return the extracted information in JSON format with the field names as keys.
2. Use the exact field names as specified above.
3. If a field can have multiple values, return them as a list.
4. Format dates in ISO format (YYYY-MM-DD) when possible.
5. Maintain the hierarchical structure of the data as defined in the fields.
6. For nested objects, use nested JSON objects.
7. For numeric values, return them as numbers without units (e.g., 42 instead of "42 years").
8. For boolean values, return true or false without quotes.
"""
    
    def build_field_extraction_prompt(
        self,
        text: str,
        domain_name: str,
        field_name: str
    ) -> str:
        """
        Build a prompt focused on extracting a single field.
        
        Args:
            text: Text to extract from
            domain_name: Domain name
            field_name: Field name to extract
            
        Returns:
            Field-specific extraction prompt
        """
        # Get domain definition
        domain = self.domain_registry.get_domain(domain_name)
        if not domain:
            raise ValueError(f"Domain '{domain_name}' not found in registry")
        
        # Find the field in any sub-domain
        field_info = domain.get_field(field_name)
        if not field_info:
            raise ValueError(f"Field '{field_name}' not found in domain '{domain_name}'")
        
        sub_domain, field = field_info
        
        # Build the prompt
        prompt = f"""# Extraction Task for {domain.name.title()} Domain - {field.name}

You are tasked with extracting the {field.name} from the following {domain.name} document.
Domain description: {domain.description}
Sub-domain: {sub_domain.description}

"""
        
        # Add field-specific extraction instructions
        prompt += f"## Field to Extract: {field.name}\n\n"
        prompt += field.to_prompt_text() + "\n"
        
        # Add anti-hallucination instructions
        prompt += self._build_anti_hallucination_instructions()
        
        # Add simplified formatting instructions
        prompt += """
## Output Format Instructions

Return the extracted information as a single JSON object with the field name as the key.
Example: {"field_name": "extracted value"}

If the field is not found, return: {"field_name": null}
"""
        
        # Add the text to extract from
        prompt += f"\nText:\n{text}\n"
        
        return prompt
