"""
Prompt Generator for the Dudoxx Extraction system.

This module provides common prompt generation functions for both the regular
and parallel extraction pipelines to ensure consistent prompt generation.
"""

from typing import List, Dict, Any, Optional, Union
from dudoxx_extraction.domains.domain_registry import DomainRegistry
from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from rich.console import Console

# Initialize console for rich logging
console = Console()

def generate_extraction_prompt(
    text: str,
    domain_name: str,
    field_names: Optional[List[str]] = None,
    sub_domain_names: Optional[List[str]] = None,
    domain_registry: Optional[DomainRegistry] = None
) -> str:
    """
    Generate an extraction prompt using the PromptBuilder.
    
    This function is used by both the regular and parallel extraction pipelines
    to ensure consistent prompt generation.
    
    Args:
        text: Text to extract from
        domain_name: Domain name
        field_names: Specific field names to extract (if None, use all fields from sub_domains)
        sub_domain_names: Sub-domain names to include (if None, use all sub-domains)
        domain_registry: Domain registry (if None, the singleton instance will be used)
        
    Returns:
        Extraction prompt
    """
    try:
        # Import here to avoid circular imports
        from dudoxx_extraction.prompt_builder import PromptBuilder
        
        # Create prompt builder
        prompt_builder = PromptBuilder(domain_registry)
        
        # Build extraction prompt
        return prompt_builder.build_extraction_prompt(
            text=text,
            domain_name=domain_name,
            field_names=field_names,
            sub_domain_names=sub_domain_names
        )
    except Exception as e:
        # Log error
        console.print(f"[red]Error generating extraction prompt: {e}[/]")
        
        # Fall back to simple prompt generation
        return generate_fallback_prompt(
            text=text,
            domain_name=domain_name,
            field_names=field_names,
            sub_domain_names=sub_domain_names,
            domain_registry=domain_registry
        )

def generate_fallback_prompt(
    text: str,
    domain_name: str,
    field_names: Optional[List[str]] = None,
    sub_domain_names: Optional[List[str]] = None,
    domain_registry: Optional[DomainRegistry] = None
) -> str:
    """
    Generate a fallback extraction prompt when PromptBuilder fails.
    
    Args:
        text: Text to extract from
        domain_name: Domain name
        field_names: Specific field names to extract (if None, use all fields from sub_domains)
        sub_domain_names: Sub-domain names to include (if None, use all sub-domains)
        domain_registry: Domain registry (if None, the singleton instance will be used)
        
    Returns:
        Fallback extraction prompt
    """
    # Get domain registry
    registry = domain_registry or DomainRegistry()
    
    # Get domain definition
    domain = registry.get_domain(domain_name)
    
    # Create field descriptions
    field_descriptions = {}
    
    if domain:
        # Get sub-domains
        if sub_domain_names:
            sub_domains = [domain.get_sub_domain(name) for name in sub_domain_names if domain.get_sub_domain(name)]
        else:
            sub_domains = domain.sub_domains
        
        # Get field descriptions from sub-domains
        for sub_domain in sub_domains:
            for field in sub_domain.fields:
                if field_names is None or field.name in field_names:
                    field_descriptions[field.name] = field.description
    
    # If no field descriptions found, use default descriptions
    if not field_descriptions:
        field_descriptions = {
            "patient_name": "Full name of the patient",
            "date_of_birth": "Patient's date of birth",
            "diagnoses": "List of diagnoses",
            "medications": "List of medications",
            "visits": "List of medical visits with dates and descriptions",
            "parties": "Parties involved in the contract",
            "effective_date": "Date when the contract becomes effective",
            "termination_date": "Date when the contract terminates",
            "obligations": "List of obligations for each party",
            "events": "List of events with dates and descriptions"
        }
    
    # Determine fields to extract
    fields_to_extract = field_names or list(field_descriptions.keys())
    
    # Create field list for prompt
    field_list = "\n".join([f"- {field}: {field_descriptions.get(field, '')}" for field in fields_to_extract])
    
    # Create anti-hallucination instructions
    anti_hallucination_instructions = """
## Important: Anti-Hallucination Instructions

1. ONLY extract information that is EXPLICITLY stated in the text.
2. If a field is not found in the text, return null for that field.
3. DO NOT infer, assume, or generate information that is not directly present in the text.
4. If you're uncertain about a value, return null rather than guessing.
5. For list-type fields, only include items that are clearly mentioned in the text.
6. Do not extract information from section headers or metadata unless it's part of the actual content.
7. If multiple conflicting values are found for a field, extract the most specific or recent one.
8. Do not use your general knowledge to fill in missing information.
9. Distinguish between definitive statements and possibilities in the text (e.g., "may have" vs "has").
10. Be precise with numerical values - do not round or approximate unless explicitly stated in the text.
"""
    
    # Add domain-specific anti-hallucination instructions if available
    if domain and domain.anti_hallucination_instructions:
        anti_hallucination_instructions += f"\n## Domain-Specific Anti-Hallucination Instructions\n\n{domain.anti_hallucination_instructions}\n"
    
    # Add subdomain-specific anti-hallucination instructions if available
    if domain and sub_domain_names:
        for sub_domain_name in sub_domain_names:
            sub_domain = domain.get_sub_domain(sub_domain_name)
            if sub_domain and sub_domain.anti_hallucination_instructions:
                anti_hallucination_instructions += f"\n## {sub_domain.name.replace('_', ' ').title()} Anti-Hallucination Instructions\n\n{sub_domain.anti_hallucination_instructions}\n"
    
    # Create prompt
    prompt = f"""Extract the following information from the {domain_name} document:

{field_list}

{anti_hallucination_instructions}

Return the information in JSON format with the field names as keys.
If a field is not found in the text, return null for that field.
If a field can have multiple values, return them as a list.

Text:
{text}
"""
    
    return prompt
