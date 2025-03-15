"""
Domain Identifier for the Dudoxx Extraction system.

This module provides functionality to identify appropriate domains and fields
for extraction based on user queries or raw text input.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the project root to the Python path when running this file directly
if __name__ == "__main__":
    # Get the absolute path of the current file
    current_file = Path(__file__).resolve()
    
    # Get the parent directory of the current file (dudoxx_extraction)
    package_dir = current_file.parent
    
    # Get the parent directory of the package directory (project root)
    project_root = package_dir.parent
    
    # Add the project root to the Python path
    sys.path.insert(0, str(project_root))

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, tool

# Local imports
from dudoxx_extraction.configuration_service import ConfigurationService
from dudoxx_extraction.domains.domain_registry import DomainRegistry


class DomainMatch(BaseModel):
    """
    Model for a matched domain.
    
    Attributes:
        domain_name: Name of the matched domain
        confidence: Confidence score for the match (0-1)
        reason: Reason for the match
    """
    domain_name: str = Field(description="Name of the matched domain")
    confidence: float = Field(description="Confidence score for the match (0-1)")
    reason: str = Field(description="Reason for the match")


class FieldMatch(BaseModel):
    """
    Model for a matched field.
    
    Attributes:
        domain_name: Name of the parent domain
        sub_domain_name: Name of the parent sub-domain
        field_name: Name of the matched field
        confidence: Confidence score for the match (0-1)
        reason: Reason for the match
    """
    domain_name: str = Field(description="Name of the parent domain")
    sub_domain_name: str = Field(description="Name of the parent sub-domain")
    field_name: str = Field(description="Name of the matched field")
    confidence: float = Field(description="Confidence score for the match (0-1)")
    reason: str = Field(description="Reason for the match")


class DomainIdentificationResult(BaseModel):
    """
    Result of domain identification.
    
    Attributes:
        matched_domains: List of matched domains
        matched_fields: List of matched fields
        recommended_domains: List of recommended domain names
        recommended_fields: Dictionary mapping domain names to lists of recommended field names
        highest_rated_domains: List of domain names sorted by confidence
        highest_rated_fields: List of field paths sorted by confidence
    """
    matched_domains: List[DomainMatch] = Field(description="List of matched domains")
    matched_fields: List[FieldMatch] = Field(description="List of matched fields")
    recommended_domains: List[str] = Field(description="List of recommended domain names")
    recommended_fields: Dict[str, List[str]] = Field(description="Dictionary mapping domain names to lists of recommended field names")
    highest_rated_domains: List[Tuple[str, float]] = Field(description="List of domain names sorted by confidence", default_factory=list)
    highest_rated_fields: List[Tuple[str, float]] = Field(description="List of field paths sorted by confidence", default_factory=list)


class DomainIdentifier:
    """
    Identifies appropriate domains and fields for extraction based on user queries.
    
    This class uses LLMs to analyze user queries and determine which domains and fields
    would be most suitable for extraction.
    """
    
    def __init__(self, llm=None, domain_registry=None, use_rich_logging=True):
        """
        Initialize the domain identifier.
        
        Args:
            llm: LangChain LLM (if None, one will be created using ConfigurationService)
            domain_registry: Domain registry (if None, the singleton instance will be used)
        """
        # Initialize rich console for logging
        self.use_rich_logging = use_rich_logging
        self.console = Console() if use_rich_logging else None
        
        # Initialize configuration service
        self.config_service = ConfigurationService()
        
        # Initialize LLM if not provided
        if llm is None:
            llm_config = self.config_service.get_llm_config()
            self.llm = ChatOpenAI(
                base_url=llm_config["base_url"],
                api_key=llm_config["api_key"],
                model_name=llm_config["model_name"],
                temperature=0.0,  # Use 0 temperature for deterministic results
                max_tokens=llm_config["max_tokens"]
            )
        else:
            self.llm = llm
        
        # Get domain registry
        self.domain_registry = domain_registry or DomainRegistry()
        
        # Create tools for domain identification
        self.tools = self._create_tools()
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for domain identification.
        
        Returns:
            List of tools
        """
        @tool
        def get_available_domains() -> Dict[str, Any]:
            """
            Get information about all available domains.
            
            Returns:
                Dictionary with domain information
            """
            domains = self.domain_registry.get_all_domains()
            domain_info = []
            
            for domain in domains:
                sub_domains = []
                for sub_domain in domain.sub_domains:
                    fields = []
                    for field in sub_domain.fields:
                        fields.append({
                            "name": field.name,
                            "description": field.description,
                            "type": field.type
                        })
                    
                    sub_domains.append({
                        "name": sub_domain.name,
                        "description": sub_domain.description,
                        "fields": fields
                    })
                
                domain_info.append({
                    "name": domain.name,
                    "description": domain.description,
                    "sub_domains": sub_domains
                })
            
            return {
                "domains": domain_info,
                "domain_count": len(domains)
            }
        
        @tool
        def match_domain_to_query(query: str, domain_name: str) -> Dict[str, Any]:
            """
            Match a domain to a user query.
            
            Args:
                query: User query
                domain_name: Domain name to match
                
            Returns:
                Dictionary with match information
            """
            domain = self.domain_registry.get_domain(domain_name)
            if domain is None:
                return {
                    "matched": False,
                    "confidence": 0.0,
                    "reason": f"Domain '{domain_name}' not found"
                }
            
            # Simple matching logic based on keywords
            query_lower = query.lower()
            domain_name_lower = domain.name.lower()
            domain_desc_lower = domain.description.lower()
            
            # Check for direct matches
            domain_name_in_query = domain_name_lower in query_lower
            domain_desc_in_query = any(word in query_lower for word in domain_desc_lower.split())
            
            # Check for domain-specific keywords
            domain_keywords = self._get_domain_keywords(domain.name)
            keyword_matches = [keyword for keyword in domain_keywords if keyword in query_lower]
            
            # Calculate confidence
            confidence = 0.0
            reasons = []
            
            if domain_name_in_query:
                confidence = max(confidence, 0.9)
                reasons.append(f"Domain name '{domain.name}' found in query")
            
            if domain_desc_in_query:
                confidence = max(confidence, 0.7)
                reasons.append(f"Domain description keywords found in query")
            
            if keyword_matches:
                confidence = max(confidence, 0.8)
                reasons.append(f"Domain keywords found: {', '.join(keyword_matches[:3])}")
            
            return {
                "matched": confidence >= 0.5,
                "confidence": confidence,
                "reason": "; ".join(reasons) if reasons else "No match found"
            }
        
        @tool
        def match_field_to_query(query: str, domain_name: str, sub_domain_name: str, field_name: str) -> Dict[str, Any]:
            """
            Match a field to a user query.
            
            Args:
                query: User query
                domain_name: Domain name
                sub_domain_name: Sub-domain name
                field_name: Field name to match
                
            Returns:
                Dictionary with match information
            """
            domain = self.domain_registry.get_domain(domain_name)
            if domain is None:
                return {
                    "matched": False,
                    "confidence": 0.0,
                    "reason": f"Domain '{domain_name}' not found"
                }
            
            sub_domain = domain.get_sub_domain(sub_domain_name)
            if sub_domain is None:
                return {
                    "matched": False,
                    "confidence": 0.0,
                    "reason": f"Sub-domain '{sub_domain_name}' not found in domain '{domain_name}'"
                }
            
            field = None
            for f in sub_domain.fields:
                if f.name == field_name:
                    field = f
                    break
            
            if field is None:
                return {
                    "matched": False,
                    "confidence": 0.0,
                    "reason": f"Field '{field_name}' not found in sub-domain '{sub_domain_name}'"
                }
            
            # Simple matching logic based on keywords
            query_lower = query.lower()
            field_name_lower = field.name.lower()
            field_desc_lower = field.description.lower()
            
            # Check for direct matches
            field_name_in_query = field_name_lower in query_lower
            field_desc_in_query = any(word in query_lower for word in field_desc_lower.split())
            
            # Check for field-specific keywords
            field_keywords = self._get_field_keywords(field.name)
            keyword_matches = [keyword for keyword in field_keywords if keyword in query_lower]
            
            # Calculate confidence
            confidence = 0.0
            reasons = []
            
            if field_name_in_query:
                confidence = max(confidence, 0.9)
                reasons.append(f"Field name '{field.name}' found in query")
            
            if field_desc_in_query:
                confidence = max(confidence, 0.7)
                reasons.append(f"Field description keywords found in query")
            
            if keyword_matches:
                confidence = max(confidence, 0.8)
                reasons.append(f"Field keywords found: {', '.join(keyword_matches[:3])}")
            
            return {
                "matched": confidence >= 0.5,
                "confidence": confidence,
                "reason": "; ".join(reasons) if reasons else "No match found"
            }
        
        return [
            get_available_domains,
            match_domain_to_query,
            match_field_to_query
        ]
    
    def _get_domain_keywords(self, domain_name: str) -> List[str]:
        """
        Get keywords for a domain from the domain registry.
        
        Args:
            domain_name: Domain name
            
        Returns:
            List of keywords
        """
        domain = self.domain_registry.get_domain(domain_name)
        if domain is None:
            return []
        
        keywords = []
        
        # Add domain name as a keyword
        keywords.append(domain_name.lower())
        
        # Add words from domain description
        if domain.description:
            keywords.extend([word.lower() for word in domain.description.split() if len(word) > 3])
        
        # Add sub-domain names and descriptions
        for sub_domain in domain.sub_domains:
            keywords.append(sub_domain.name.lower())
            if sub_domain.description:
                keywords.extend([word.lower() for word in sub_domain.description.split() if len(word) > 3])
        
        # Add field names from all sub-domains
        for sub_domain in domain.sub_domains:
            for field in sub_domain.fields:
                keywords.append(field.name.lower())
                
                # Add words from field description
                if field.description:
                    keywords.extend([word.lower() for word in field.description.split() if len(word) > 3])
        
        # Remove duplicates and common words
        common_words = {"the", "and", "for", "with", "this", "that", "from", "have", "has", "been", "were", "are", "will"}
        keywords = [kw for kw in keywords if kw not in common_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _get_field_keywords(self, field_name: str, domain_name: str = None, sub_domain_name: str = None) -> List[str]:
        """
        Get keywords for a field from the domain registry.
        
        Args:
            field_name: Field name
            domain_name: Domain name (optional)
            sub_domain_name: Sub-domain name (optional)
            
        Returns:
            List of keywords
        """
        keywords = []
        
        # Add field name as a keyword
        keywords.append(field_name.lower())
        
        # Split field name into words and add them as keywords
        words = field_name.replace('_', ' ').split()
        keywords.extend([word.lower() for word in words if len(word) > 2])
        
        # If domain and sub-domain are provided, get field from registry
        if domain_name and sub_domain_name:
            domain = self.domain_registry.get_domain(domain_name)
            if domain:
                sub_domain = domain.get_sub_domain(sub_domain_name)
                if sub_domain:
                    for field in sub_domain.fields:
                        if field.name == field_name:
                            # Add words from field description
                            if field.description:
                                desc_words = field.description.split()
                                keywords.extend([word.lower() for word in desc_words if len(word) > 2])
                            
                            # Add examples as keywords if available
                            if field.examples:
                                for example in field.examples:
                                    if isinstance(example, str):
                                        example_words = example.split()
                                        keywords.extend([word.lower() for word in example_words if len(word) > 2])
                                    elif isinstance(example, dict):
                                        # For dictionary examples, add values as keywords
                                        for value in example.values():
                                            if isinstance(value, str):
                                                value_words = value.split()
                                                keywords.extend([word.lower() for word in value_words if len(word) > 2])
        
        # Remove duplicates and common words
        common_words = {"the", "and", "for", "with", "this", "that", "from", "have", "has", "been", "were", "are", "will"}
        keywords = [kw for kw in keywords if kw not in common_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def identify_domains_for_query(self, query: str) -> DomainIdentificationResult:
        """
        Identify domains and fields for a user query.
        
        Args:
            query: User query
            
        Returns:
            DomainIdentificationResult with identified domains and fields
        """
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a domain identification expert. Your task is to analyze the given user query and identify which domains and fields would be most appropriate for extracting the requested information.

Use the provided tools to:
1. Get information about available domains
2. Match domains to the query
3. Match fields to the query

After using the tools, provide a final recommendation of which domains and fields to use for extraction.

Be thorough in your analysis and provide clear reasoning for your recommendations."""),
            ("human", "Please analyze the following user query and identify appropriate domains and fields for extraction:\n\n{query}")
        ])
        
        # Create chain
        chain = prompt | self.llm_with_tools
        
        # Run chain
        response = chain.invoke({"query": query})
        
        # Process the response to extract domain and field matches
        matched_domains = []
        matched_fields = []
        
        # Get all domains from the registry
        domains = self.domain_registry.get_all_domains()
        
        # For each domain, check if it matches the query
        for domain in domains:
            # Match domain to query
            domain_match = self.match_domain_to_query(query, domain.name)
            
            if domain_match.get("matched", False):
                matched_domains.append(DomainMatch(
                    domain_name=domain.name,
                    confidence=domain_match.get("confidence", 0.0),
                    reason=domain_match.get("reason", "")
                ))
                
                # For each sub-domain in the matched domain, check fields
                for sub_domain in domain.sub_domains:
                    for field in sub_domain.fields:
                        # Match field to query
                        field_match = self.match_field_to_query(query, domain.name, sub_domain.name, field.name)
                        
                        if field_match.get("matched", False):
                            matched_fields.append(FieldMatch(
                                domain_name=domain.name,
                                sub_domain_name=sub_domain.name,
                                field_name=field.name,
                                confidence=field_match.get("confidence", 0.0),
                                reason=field_match.get("reason", "")
                            ))
        
        # Create recommendations based on matches
        recommended_domains = [match.domain_name for match in matched_domains]
        
        recommended_fields = {}
        for match in matched_fields:
            if match.domain_name not in recommended_fields:
                recommended_fields[match.domain_name] = []
            recommended_fields[match.domain_name].append(f"{match.sub_domain_name}.{match.field_name}")
        
        # Sort domains by confidence
        sorted_domains = sorted(
            [(match.domain_name, match.confidence) for match in matched_domains],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Sort fields by confidence
        sorted_fields = sorted(
            [(f"{match.domain_name}.{match.sub_domain_name}.{match.field_name}", match.confidence) 
             for match in matched_fields],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Create result
        result = DomainIdentificationResult(
            matched_domains=matched_domains,
            matched_fields=matched_fields,
            recommended_domains=recommended_domains,
            recommended_fields=recommended_fields,
            highest_rated_domains=sorted_domains,
            highest_rated_fields=sorted_fields
        )
        
        # Log the result if rich logging is enabled
        if self.use_rich_logging:
            self._log_identification_result(query, result)
        
        return result
    
    def _log_identification_result(self, query: str, result: DomainIdentificationResult) -> None:
        """
        Log the domain identification result using rich formatting.
        
        Args:
            query: The original query
            result: The domain identification result
        """
        self.console.print(Panel(f"Domain Identification for Query: {query}", style="bold magenta"))
        
        # Display matched domains
        self.console.print("\n[bold]Matched Domains:[/]")
        if result.matched_domains:
            domains_table = Table(title="Domain Matches")
            domains_table.add_column("Domain", style="cyan")
            domains_table.add_column("Confidence", style="green")
            domains_table.add_column("Reason", style="yellow")
            
            for match in result.matched_domains:
                domains_table.add_row(
                    match.domain_name,
                    f"{match.confidence:.2f}",
                    match.reason
                )
            
            self.console.print(domains_table)
        else:
            self.console.print("[yellow]No domain matches found[/]")
        
        # Display highest rated domains
        self.console.print("\n[bold]Highest Rated Domains:[/]")
        if result.highest_rated_domains:
            domains_table = Table(title="Top Domains by Confidence")
            domains_table.add_column("Domain", style="cyan")
            domains_table.add_column("Confidence", style="green")
            
            for domain_name, confidence in result.highest_rated_domains:
                domains_table.add_row(
                    domain_name,
                    f"{confidence:.2f}"
                )
            
            self.console.print(domains_table)
        
        # Display highest rated fields
        self.console.print("\n[bold]Highest Rated Fields:[/]")
        if result.highest_rated_fields:
            fields_table = Table(title="Top Fields by Confidence")
            fields_table.add_column("Field Path", style="cyan")
            fields_table.add_column("Confidence", style="green")
            
            for field_path, confidence in result.highest_rated_fields[:10]:  # Show top 10 fields
                fields_table.add_row(
                    field_path,
                    f"{confidence:.2f}"
                )
            
            self.console.print(fields_table)
        
        # Display recommendations
        self.console.print("\n[bold]Recommendations:[/]")
        self.console.print(f"Recommended domains: {', '.join(result.recommended_domains)}")
        
        for domain, fields in result.recommended_fields.items():
            self.console.print(f"Recommended fields for {domain}: {', '.join(fields)}")
    
    def match_domain_to_query(self, query: str, domain_name: str) -> Dict[str, Any]:
        """
        Match a domain to a user query with improved specificity.
        
        Args:
            query: User query
            domain_name: Domain name to match
            
        Returns:
            Dictionary with match information
        """
        domain = self.domain_registry.get_domain(domain_name)
        if domain is None:
            return {
                "matched": False,
                "confidence": 0.0,
                "reason": f"Domain '{domain_name}' not found"
            }
        
        # Enhanced matching logic
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        domain_name_lower = domain.name.lower()
        domain_desc_lower = domain.description.lower()
        
        # Check for exact phrase matches (higher confidence)
        exact_phrase_matches = []
        if domain_name_lower in query_lower:
            exact_phrase_matches.append(domain_name_lower)
        
        # Check for domain-specific keywords with more context
        domain_keywords = self._get_domain_keywords(domain.name)
        
        # Count keyword matches and their positions
        keyword_matches = []
        multi_word_matches = 0
        
        for keyword in domain_keywords:
            if keyword in query_lower:
                keyword_matches.append(keyword)
                
                # Check if multi-word keywords match (higher confidence)
                if len(keyword.split()) > 1:
                    multi_word_matches += 1
        
        # Calculate semantic relevance
        domain_terms = set(domain_name_lower.split() + domain_desc_lower.split())
        term_overlap = len(query_terms.intersection(domain_terms))
        term_overlap_ratio = term_overlap / len(query_terms) if query_terms else 0
        
        # Calculate confidence with more nuanced approach
        confidence = 0.0
        reasons = []
        
        # Domain name in query is a strong signal
        if domain_name_lower in query_lower:
            confidence = max(confidence, 0.9)
            reasons.append(f"Domain name '{domain.name}' found in query")
        
        # Exact phrase matches are very strong signals
        if exact_phrase_matches:
            confidence = max(confidence, 0.95)
            reasons.append(f"Exact phrase matches: {', '.join(exact_phrase_matches)}")
        
        # Multi-word keyword matches are strong signals
        if multi_word_matches > 0:
            confidence = max(confidence, 0.85)
            reasons.append(f"Multi-word keyword matches found")
        
        # Regular keyword matches
        if keyword_matches:
            # Scale confidence based on number of matches
            match_confidence = min(0.7 + (len(keyword_matches) * 0.05), 0.9)
            confidence = max(confidence, match_confidence)
            reasons.append(f"Domain keywords found: {', '.join(keyword_matches[:3])}")
        
        # Term overlap ratio provides additional signal
        if term_overlap_ratio > 0.5:
            confidence = max(confidence, 0.75)
            reasons.append(f"High term overlap ratio: {term_overlap_ratio:.2f}")
        
        # Higher threshold for matching
        return {
            "matched": confidence >= 0.6,  # Increased threshold
            "confidence": confidence,
            "reason": "; ".join(reasons) if reasons else "No match found"
        }
    
    def match_field_to_query(self, query: str, domain_name: str, sub_domain_name: str, field_name: str) -> Dict[str, Any]:
        """
        Match a field to a user query.
        
        Args:
            query: User query
            domain_name: Domain name
            sub_domain_name: Sub-domain name
            field_name: Field name to match
            
        Returns:
            Dictionary with match information
        """
        domain = self.domain_registry.get_domain(domain_name)
        if domain is None:
            return {
                "matched": False,
                "confidence": 0.0,
                "reason": f"Domain '{domain_name}' not found"
            }
        
        sub_domain = domain.get_sub_domain(sub_domain_name)
        if sub_domain is None:
            return {
                "matched": False,
                "confidence": 0.0,
                "reason": f"Sub-domain '{sub_domain_name}' not found in domain '{domain_name}'"
            }
        
        field = None
        for f in sub_domain.fields:
            if f.name == field_name:
                field = f
                break
        
        if field is None:
            return {
                "matched": False,
                "confidence": 0.0,
                "reason": f"Field '{field_name}' not found in sub-domain '{sub_domain_name}'"
            }
        
        # Simple matching logic based on keywords
        query_lower = query.lower()
        field_name_lower = field.name.lower()
        field_desc_lower = field.description.lower()
        
        # Check for direct matches
        field_name_in_query = field_name_lower in query_lower
        field_desc_in_query = any(word in query_lower for word in field_desc_lower.split())
        
        # Check for field-specific keywords
        field_keywords = self._get_field_keywords(field.name, domain_name, sub_domain_name)
        keyword_matches = [keyword for keyword in field_keywords if keyword in query_lower]
        
        # Calculate confidence
        confidence = 0.0
        reasons = []
        
        if field_name_in_query:
            confidence = max(confidence, 0.9)
            reasons.append(f"Field name '{field.name}' found in query")
        
        if field_desc_in_query:
            confidence = max(confidence, 0.7)
            reasons.append(f"Field description keywords found in query")
        
        if keyword_matches:
            confidence = max(confidence, 0.8)
            reasons.append(f"Field keywords found: {', '.join(keyword_matches[:3])}")
        
        return {
            "matched": confidence >= 0.5,
            "confidence": confidence,
            "reason": "; ".join(reasons) if reasons else "No match found"
        }


    def get_extraction_schema(self, query: str) -> Dict[str, Dict[str, List[Tuple[str, float]]]]:
        """
        Get a recommended extraction schema for a query using LLM.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with recommended extraction schema
        """
        # Create a prompt for the LLM to directly identify the most relevant domains and fields
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a domain identification expert. Your task is to analyze the given user query and identify ONLY the most relevant domain and fields that are EXPLICITLY requested.

Be extremely precise and focused on EXACTLY what the user is asking for. Do not include any domains or fields that are not directly mentioned or clearly implied by the query.

For example:
- If the query is "What is the patient's name?", you should ONLY identify the medical domain and the patient_name field.
- If the query is "What medications is the patient taking?", you should ONLY identify the medical domain and the medications field.

DO NOT include additional fields that might be "nice to have" but weren't requested. Be minimalist and precise.

Available domains include:
- medical: For medical records, patient information, diagnoses, etc.
- legal: For legal documents, contracts, agreements, etc.
- demographic: For personal and organizational information
- general: For general content that doesn't fit other domains

Each domain has multiple sub-domains with specific fields. Focus only on what's explicitly requested.

Return your answer in this exact format:
{{
  "domain": "name_of_primary_domain",
  "sub_domains": {{
    "sub_domain_name": ["field1", "field2"]
  }}
}}

Include ONLY ONE domain and ONLY the fields that are DIRECTLY requested in the query."""),
            ("human", "Query: {query}")
        ])
        
        # Create chain
        chain = prompt | self.llm
        
        # Run chain
        response = chain.invoke({"query": query})
        
        # Parse the response to extract domain and fields
        try:
            # Try to extract JSON from the response
            import re
            import json
            
            # Look for JSON pattern in the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_response = json.loads(json_str)
                
                domain = parsed_response.get("domain")
                sub_domains = parsed_response.get("sub_domains", {})
                
                # Convert to extraction schema format
                extraction_schema = {}
                if domain:
                    extraction_schema[domain] = {}
                    for sub_domain, fields in sub_domains.items():
                        extraction_schema[domain][sub_domain] = [(field, 1.0) for field in fields]
            else:
                # Fallback to a simple domain identification
                result = self.identify_domains_for_query(query)
                if result.recommended_domains:
                    domain = result.recommended_domains[0]
                    extraction_schema = {domain: {}}
                    
                    # Get fields for this domain
                    if domain in result.recommended_fields:
                        for field_path in result.recommended_fields[domain]:
                            parts = field_path.split('.')
                            if len(parts) == 2:
                                sub_domain, field = parts
                                if sub_domain not in extraction_schema[domain]:
                                    extraction_schema[domain][sub_domain] = []
                                extraction_schema[domain][sub_domain].append((field, 0.9))
                else:
                    # Default to general domain if nothing is identified
                    extraction_schema = {"general": {"default": [("content", 0.8)]}}
        except Exception as e:
            # Fallback to a simple domain identification
            self.console.print(f"[red]Error parsing LLM response: {e}[/]")
            self.console.print(f"[yellow]Response: {response.content}[/]")
            
            # Use a simplified approach
            result = self.identify_domains_for_query(query)
            if result.recommended_domains:
                domain = result.recommended_domains[0]
                extraction_schema = {domain: {}}
                
                # Get fields for this domain
                if domain in result.recommended_fields:
                    for field_path in result.recommended_fields[domain]:
                        parts = field_path.split('.')
                        if len(parts) == 2:
                            sub_domain, field = parts
                            if sub_domain not in extraction_schema[domain]:
                                extraction_schema[domain][sub_domain] = []
                            extraction_schema[domain][sub_domain].append((field, 0.9))
            else:
                # Default to general domain if nothing is identified
                extraction_schema = {"general": {"default": [("content", 0.8)]}}
        
        # Log the extraction schema if rich logging is enabled
        if self.use_rich_logging:
            self._log_extraction_schema(query, extraction_schema)
        
        return extraction_schema
    
    def _log_extraction_schema(self, query: str, extraction_schema: Dict[str, Dict[str, List[Tuple[str, float]]]]) -> None:
        """
        Log the extraction schema using rich formatting.
        
        Args:
            query: The original query
            extraction_schema: The extraction schema
        """
        self.console.print(Panel(f"Recommended Extraction Schema for Query: {query}", style="bold green"))
        
        for domain_name, sub_domains in extraction_schema.items():
            self.console.print(f"[bold cyan]{domain_name}[/]")
            
            for sub_domain_name, fields in sub_domains.items():
                self.console.print(f"  [green]{sub_domain_name}[/]")
                
                # Sort fields by confidence
                sorted_fields = sorted(fields, key=lambda x: x[1], reverse=True)
                
                for field_name, confidence in sorted_fields:
                    self.console.print(f"    [yellow]{field_name}[/] ([magenta]{confidence:.2f}[/])")


# Example usage
if __name__ == "__main__":
    # Create domain identifier
    domain_identifier = DomainIdentifier(use_rich_logging=True)
    
    # Example query
    query = "What are the patient information?"
    
    # Identify domains and fields
    result = domain_identifier.identify_domains_for_query(query)
    
    # Get extraction schema
    extraction_schema = domain_identifier.get_extraction_schema(query)
