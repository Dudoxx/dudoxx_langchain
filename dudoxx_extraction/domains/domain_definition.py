"""
Domain definition classes for the Dudoxx Extraction system.

This module provides enhanced classes for defining domains, sub-domains, and fields
for the extraction system with additional attributes for improved extraction,
formatting, validation, and post-processing.
"""

from typing import List, Dict, Any, Optional, Union, Tuple, Pattern, Callable
from pydantic import BaseModel, Field, validator
import re
from enum import Enum


class ValidationLevel(str, Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class FieldDefinition(BaseModel):
    """
    Enhanced definition of a field to extract.
    
    Attributes:
        name: Name of the field
        description: Description of the field
        type: Type of the field (string, number, date, list, etc.)
        is_required: Whether the field is required
        is_unique: Whether the field should have a unique value
        examples: Example values for the field
        extraction_instructions: Specific instructions for extracting this field
        formatting_instructions: Instructions for formatting the extracted value
        validation_rules: Rules for validating the extracted value
        validation_level: Severity level for validation failures
        format_pattern: Regex pattern for the field format
        format_function: Function to format the extracted value
        validation_function: Function to validate the extracted value
        post_process_function: Function to post-process the extracted value
        related_fields: Names of related fields
        context_window: Number of tokens/characters to consider around potential matches
        keywords: Keywords that often appear near this field
        negative_keywords: Keywords that suggest this field is NOT present
        extraction_priority: Priority for extraction (higher values = higher priority)
        confidence_threshold: Minimum confidence score to accept an extraction
    """
    
    name: str = Field(description="Name of the field")
    description: str = Field(description="Description of the field")
    type: str = Field(description="Type of the field (string, number, date, list, etc.)")
    is_required: bool = Field(default=False, description="Whether the field is required")
    is_unique: bool = Field(default=False, description="Whether the field should have a unique value")
    examples: Optional[List[Any]] = Field(default=None, description="Example values for the field")
    
    # New extraction-specific attributes
    extraction_instructions: Optional[str] = Field(
        default=None, 
        description="Specific instructions for extracting this field"
    )
    context_window: Optional[int] = Field(
        default=None, 
        description="Number of tokens/characters to consider around potential matches"
    )
    keywords: Optional[List[str]] = Field(
        default=None, 
        description="Keywords that often appear near this field"
    )
    negative_keywords: Optional[List[str]] = Field(
        default=None, 
        description="Keywords that suggest this field is NOT present"
    )
    extraction_priority: Optional[int] = Field(
        default=None, 
        description="Priority for extraction (higher values = higher priority)"
    )
    confidence_threshold: Optional[float] = Field(
        default=None, 
        description="Minimum confidence score to accept an extraction"
    )
    
    # New formatting-specific attributes
    formatting_instructions: Optional[str] = Field(
        default=None, 
        description="Instructions for formatting the extracted value"
    )
    format_pattern: Optional[str] = Field(
        default=None, 
        description="Regex pattern for the field format"
    )
    format_function: Optional[str] = Field(
        default=None, 
        description="Name of function to format the extracted value"
    )
    
    # New validation-specific attributes
    validation_rules: Optional[List[str]] = Field(
        default=None, 
        description="Rules for validating the extracted value"
    )
    validation_level: ValidationLevel = Field(
        default=ValidationLevel.WARNING, 
        description="Severity level for validation failures"
    )
    validation_function: Optional[str] = Field(
        default=None, 
        description="Name of function to validate the extracted value"
    )
    
    # New post-processing attributes
    post_process_function: Optional[str] = Field(
        default=None, 
        description="Name of function to post-process the extracted value"
    )
    
    # Relationship attributes
    related_fields: Optional[List[str]] = Field(
        default=None, 
        description="Names of related fields"
    )
    
    def to_prompt_text(self) -> str:
        """
        Convert the field definition to prompt text.
        
        Returns:
            str: Prompt text for the field
        """
        # Start with basic field information
        prompt = f"- {self.name}: {self.description}"
        
        # Add type information
        prompt += f" (Type: {self.type})"
        
        # Add examples if available
        if self.examples:
            examples_str = ", ".join([str(example) for example in self.examples])
            prompt += f" (Examples: {examples_str})"
        
        # Add extraction instructions if available
        if self.extraction_instructions:
            prompt += f"\n  Extraction: {self.extraction_instructions}"
        
        # Add keywords if available
        if self.keywords:
            keywords_str = ", ".join(self.keywords)
            prompt += f"\n  Look for keywords: {keywords_str}"
        
        # Add required/unique indicators
        if self.is_required:
            prompt += " [REQUIRED]"
        if self.is_unique:
            prompt += " [UNIQUE]"
        
        return prompt
    
    def get_compiled_pattern(self) -> Optional[Pattern]:
        """
        Get compiled regex pattern if format_pattern is defined.
        
        Returns:
            Optional[Pattern]: Compiled regex pattern or None
        """
        if self.format_pattern:
            try:
                return re.compile(self.format_pattern)
            except re.error:
                return None
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert field definition to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return self.dict(exclude_none=True)


class SubDomainDefinition(BaseModel):
    """
    Enhanced definition of a sub-domain for extraction.
    
    A sub-domain is a smaller, focused set of fields to extract.
    
    Attributes:
        name: Name of the sub-domain
        description: Description of the sub-domain
        fields: List of fields to extract
        extraction_instructions: Specific instructions for extracting this sub-domain
        pre_extraction_function: Function to run before extraction
        post_extraction_function: Function to run after extraction
        confidence_threshold: Minimum confidence score to accept sub-domain extraction
        priority: Priority for extraction (higher values = higher priority)
        anti_hallucination_instructions: Specific anti-hallucination instructions for this sub-domain
    """
    
    name: str = Field(description="Name of the sub-domain")
    description: str = Field(description="Description of the sub-domain")
    fields: List[FieldDefinition] = Field(description="List of fields to extract")
    
    # New attributes
    extraction_instructions: Optional[str] = Field(
        default=None, 
        description="Specific instructions for extracting this sub-domain"
    )
    pre_extraction_function: Optional[str] = Field(
        default=None, 
        description="Name of function to run before extraction"
    )
    post_extraction_function: Optional[str] = Field(
        default=None, 
        description="Name of function to run after extraction"
    )
    confidence_threshold: Optional[float] = Field(
        default=None, 
        description="Minimum confidence score to accept sub-domain extraction"
    )
    priority: Optional[int] = Field(
        default=None, 
        description="Priority for extraction (higher values = higher priority)"
    )
    anti_hallucination_instructions: Optional[str] = Field(
        default=None, 
        description="Specific anti-hallucination instructions for this sub-domain"
    )
    
    def to_prompt_text(self) -> str:
        """
        Convert the sub-domain definition to prompt text.
        
        Returns:
            str: Prompt text for the sub-domain
        """
        prompt = f"Extract the following information for {self.description}:\n\n"
        
        # Add extraction instructions if available
        if self.extraction_instructions:
            prompt += f"{self.extraction_instructions}\n\n"
        
        # Add fields
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
    
    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """
        Get a field by name.
        
        Args:
            name: Name of the field
            
        Returns:
            Optional[FieldDefinition]: Field definition or None if not found
        """
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert sub-domain definition to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = {
            "name": self.name,
            "description": self.description,
            "fields": [field.to_dict() for field in self.fields]
        }
        
        if self.extraction_instructions:
            result["extraction_instructions"] = self.extraction_instructions
        if self.pre_extraction_function:
            result["pre_extraction_function"] = self.pre_extraction_function
        if self.post_extraction_function:
            result["post_extraction_function"] = self.post_extraction_function
        if self.confidence_threshold is not None:
            result["confidence_threshold"] = self.confidence_threshold
        if self.priority is not None:
            result["priority"] = self.priority
            
        return result


class DomainDefinition(BaseModel):
    """
    Enhanced definition of a domain for extraction.
    
    A domain contains multiple sub-domains, each with its own set of fields.
    
    Attributes:
        name: Name of the domain
        description: Description of the domain
        sub_domains: List of sub-domains
        extraction_instructions: General instructions for extracting from this domain
        pre_extraction_function: Function to run before extraction
        post_extraction_function: Function to run after extraction
        validation_function: Function to validate the extracted domain data
        merge_function: Function to merge results from multiple chunks
        keywords: Keywords that often appear in documents of this domain
        confidence_threshold: Minimum confidence score to accept domain identification
        anti_hallucination_instructions: General anti-hallucination instructions for this domain
    """
    
    name: str = Field(description="Name of the domain")
    description: str = Field(description="Description of the domain")
    sub_domains: List[SubDomainDefinition] = Field(description="List of sub-domains")
    
    # New attributes
    extraction_instructions: Optional[str] = Field(
        default=None, 
        description="General instructions for extracting from this domain"
    )
    pre_extraction_function: Optional[str] = Field(
        default=None, 
        description="Name of function to run before extraction"
    )
    post_extraction_function: Optional[str] = Field(
        default=None, 
        description="Name of function to run after extraction"
    )
    validation_function: Optional[str] = Field(
        default=None, 
        description="Name of function to validate the extracted domain data"
    )
    merge_function: Optional[str] = Field(
        default=None, 
        description="Name of function to merge results from multiple chunks"
    )
    keywords: Optional[List[str]] = Field(
        default=None, 
        description="Keywords that often appear in documents of this domain"
    )
    confidence_threshold: Optional[float] = Field(
        default=None, 
        description="Minimum confidence score to accept domain identification"
    )
    anti_hallucination_instructions: Optional[str] = Field(
        default=None, 
        description="General anti-hallucination instructions for this domain"
    )
    
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
    
    def get_field(self, field_name: str) -> Optional[Tuple[SubDomainDefinition, FieldDefinition]]:
        """
        Get a field by name from any sub-domain.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Optional[Tuple[SubDomainDefinition, FieldDefinition]]: Tuple of sub-domain and field or None if not found
        """
        for sub_domain in self.sub_domains:
            field = sub_domain.get_field(field_name)
            if field:
                return (sub_domain, field)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert domain definition to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = {
            "name": self.name,
            "description": self.description,
            "sub_domains": [sub_domain.to_dict() for sub_domain in self.sub_domains]
        }
        
        if self.extraction_instructions:
            result["extraction_instructions"] = self.extraction_instructions
        if self.pre_extraction_function:
            result["pre_extraction_function"] = self.pre_extraction_function
        if self.post_extraction_function:
            result["post_extraction_function"] = self.post_extraction_function
        if self.validation_function:
            result["validation_function"] = self.validation_function
        if self.merge_function:
            result["merge_function"] = self.merge_function
        if self.keywords:
            result["keywords"] = self.keywords
        if self.confidence_threshold is not None:
            result["confidence_threshold"] = self.confidence_threshold
            
        return result
