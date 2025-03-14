"""
Domain definition classes for the Dudoxx Extraction system.

This module provides classes for defining domains, sub-domains, and fields
for the extraction system.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class FieldDefinition(BaseModel):
    """
    Definition of a field to extract.
    
    Attributes:
        name: Name of the field
        description: Description of the field
        type: Type of the field (string, number, date, list, etc.)
        is_required: Whether the field is required
        is_unique: Whether the field should have a unique value
        examples: Example values for the field
    """
    
    name: str = Field(description="Name of the field")
    description: str = Field(description="Description of the field")
    type: str = Field(description="Type of the field (string, number, date, list, etc.)")
    is_required: bool = Field(default=False, description="Whether the field is required")
    is_unique: bool = Field(default=False, description="Whether the field should have a unique value")
    examples: Optional[List[Any]] = Field(default=None, description="Example values for the field")
    
    def to_prompt_text(self) -> str:
        """
        Convert the field definition to prompt text.
        
        Returns:
            str: Prompt text for the field
        """
        prompt = f"- {self.name}: {self.description}"
        
        if self.examples:
            examples_str = ", ".join([str(example) for example in self.examples])
            prompt += f" (Examples: {examples_str})"
            
        return prompt


class SubDomainDefinition(BaseModel):
    """
    Definition of a sub-domain for extraction.
    
    A sub-domain is a smaller, focused set of fields to extract.
    
    Attributes:
        name: Name of the sub-domain
        description: Description of the sub-domain
        fields: List of fields to extract
    """
    
    name: str = Field(description="Name of the sub-domain")
    description: str = Field(description="Description of the sub-domain")
    fields: List[FieldDefinition] = Field(description="List of fields to extract")
    
    def to_prompt_text(self) -> str:
        """
        Convert the sub-domain definition to prompt text.
        
        Returns:
            str: Prompt text for the sub-domain
        """
        prompt = f"Extract the following information for {self.description}:\n\n"
        
        for field in self.fields:
            prompt += field.to_prompt_text() + "\n"
            
        return prompt
    
    def get_field_names(self) -> List[str]:
        """
        Get the names of all fields in the sub-domain.
        
        Returns:
            List[str]: List of field names
        """
        return [field.name for field in self.fields]


class DomainDefinition(BaseModel):
    """
    Definition of a domain for extraction.
    
    A domain contains multiple sub-domains, each with its own set of fields.
    
    Attributes:
        name: Name of the domain
        description: Description of the domain
        sub_domains: List of sub-domains
    """
    
    name: str = Field(description="Name of the domain")
    description: str = Field(description="Description of the domain")
    sub_domains: List[SubDomainDefinition] = Field(description="List of sub-domains")
    
    def get_sub_domain(self, name: str) -> Optional[SubDomainDefinition]:
        """
        Get a sub-domain by name.
        
        Args:
            name: Name of the sub-domain
            
        Returns:
            Optional[SubDomainDefinition]: Sub-domain definition or None if not found
        """
        for sub_domain in self.sub_domains:
            if sub_domain.name == name:
                return sub_domain
                
        return None
    
    def get_all_field_names(self) -> List[str]:
        """
        Get the names of all fields in all sub-domains.
        
        Returns:
            List[str]: List of field names
        """
        field_names = []
        
        for sub_domain in self.sub_domains:
            field_names.extend(sub_domain.get_field_names())
            
        return field_names
