"""
Query Preprocessor for the Dudoxx Extraction system.

This module provides functionality to preprocess user queries using an LLM
to improve domain and field identification for all extraction flows.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

# Local imports
from dudoxx_extraction.configuration_service import ConfigurationService
from dudoxx_extraction.domains.domain_registry import DomainRegistry


class PreprocessedQuery(BaseModel):
    """
    Model for a preprocessed query.
    
    Attributes:
        original_query: The original user query
        reformulated_query: The reformulated query optimized for extraction
        identified_domain: The primary domain identified in the query
        identified_fields: List of fields identified in the query
        extraction_requirements: Structured extraction requirements
        confidence: Confidence score for the preprocessing (0-1)
    """
    original_query: str = Field(description="The original user query")
    reformulated_query: str = Field(description="The reformulated query optimized for extraction")
    identified_domain: Optional[str] = Field(None, description="The primary domain identified in the query")
    identified_fields: List[str] = Field(default_factory=list, description="List of fields identified in the query")
    extraction_requirements: Dict[str, Any] = Field(default_factory=dict, description="Structured extraction requirements")
    confidence: float = Field(default=0.0, description="Confidence score for the preprocessing (0-1)")


class QueryPreprocessor:
    """
    Preprocesses user queries using an LLM to improve domain and field identification.
    
    This class uses an LLM to analyze and reformulate user queries, identify domains and fields,
    and structure extraction requirements before passing them to the extraction pipelines.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the query preprocessor or return the existing one (singleton pattern).
        
        Returns:
            QueryPreprocessor: Query preprocessor instance
        """
        if cls._instance is None:
            cls._instance = super(QueryPreprocessor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, llm=None, domain_registry=None, use_rich_logging=True):
        """
        Initialize the query preprocessor.
        
        Args:
            llm: LangChain LLM (if None, one will be created using ConfigurationService)
            domain_registry: Domain registry (if None, the singleton instance will be used)
            use_rich_logging: Whether to use rich logging
        """
        # Only initialize once (singleton pattern)
        if getattr(self, '_initialized', False):
            return
        
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
        
        # Create domain information for the meta prompt
        self.domain_info = self._create_domain_info()
        
        # Mark as initialized
        self._initialized = True
    
    def _create_domain_info(self) -> str:
        """
        Create domain information for the meta prompt.
        
        Returns:
            str: Formatted domain information
        """
        domains = self.domain_registry.get_all_domains()
        
        domain_info = "Available domains and fields:\n\n"
        
        for domain in domains:
            domain_info += f"Domain: {domain.name}\n"
            domain_info += f"Description: {domain.description}\n"
            
            for sub_domain in domain.sub_domains:
                domain_info += f"  Sub-domain: {sub_domain.name}\n"
                domain_info += f"  Description: {sub_domain.description}\n"
                
                for field in sub_domain.fields:
                    domain_info += f"    Field: {field.name}\n"
                    domain_info += f"    Description: {field.description}\n"
                    domain_info += f"    Type: {field.type}\n"
                    
                    if field.examples:
                        examples_str = ", ".join([str(example) for example in field.examples[:2]])
                        domain_info += f"    Examples: {examples_str}\n"
                    
                    domain_info += "\n"
                
                domain_info += "\n"
            
            domain_info += "\n"
        
        return domain_info
    
    def preprocess_query(self, query: str) -> PreprocessedQuery:
        """
        Preprocess a user query using the LLM.
        
        Args:
            query: User query
            
        Returns:
            PreprocessedQuery: Preprocessed query
        """
        if self.use_rich_logging:
            self.console.print(Panel(f"Preprocessing Query: {query}", style="bold blue"))
        
        # Create system message without format specifiers
        system_message = "You are a query preprocessing expert for an information extraction system. Your task is to analyze user queries and reformulate them to improve domain and field identification.\n\n"
        system_message += self.domain_info + "\n\n"
        system_message += "For the given user query, you need to:\n"
        system_message += "1. Analyze the query to understand what information the user wants to extract\n"
        system_message += "2. Identify the most relevant domain and fields based on the available domains and fields\n"
        system_message += "3. Reformulate the query to make it more precise and focused on the specific extraction requirements\n"
        system_message += "4. Structure the extraction requirements in a clear and organized way\n\n"
        system_message += "The user query may be a single question, a list of requirements, or a full sentence. Your job is to process it into a format that will improve the extraction process.\n\n"
        system_message += "Return your analysis in the following JSON format:\n"
        system_message += "```json\n"
        system_message += "{\n"
        system_message += '  "reformulated_query": "The reformulated query optimized for extraction",\n'
        system_message += '  "identified_domain": "The primary domain identified in the query",\n'
        system_message += '  "identified_fields": ["field1", "field2"],\n'
        system_message += '  "extraction_requirements": {\n'
        system_message += '    "requirement1": "description1",\n'
        system_message += '    "requirement2": "description2"\n'
        system_message += "  },\n"
        system_message += '  "confidence": 0.95\n'
        system_message += "}\n"
        system_message += "```\n\n"
        system_message += "Be precise and focused on EXACTLY what the user is asking for. Do not include any domains or fields that are not directly mentioned or clearly implied by the query."
        
        # Create user message
        user_message = f"User Query: {query}"
        
        # Use the LLM directly without a template
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM directly
        response = self.llm.invoke(messages)
        
        # Parse the response to extract the preprocessed query
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_response = json.loads(json_str)
                
                # Create preprocessed query
                preprocessed_query = PreprocessedQuery(
                    original_query=query,
                    reformulated_query=parsed_response.get("reformulated_query", query),
                    identified_domain=parsed_response.get("identified_domain"),
                    identified_fields=parsed_response.get("identified_fields", []),
                    extraction_requirements=parsed_response.get("extraction_requirements", {}),
                    confidence=parsed_response.get("confidence", 0.0)
                )
                
                if self.use_rich_logging:
                    self._log_preprocessed_query(preprocessed_query)
                
                return preprocessed_query
            else:
                # Fallback if JSON parsing fails
                if self.use_rich_logging:
                    self.console.print("[yellow]Warning: Failed to parse JSON from LLM response[/]")
                    self.console.print(f"[yellow]Response: {response.content}[/]")
                
                preprocessed_query = PreprocessedQuery(
                    original_query=query,
                    reformulated_query=query,
                    confidence=0.0
                )
                
                return preprocessed_query
        except Exception as e:
            # Fallback if any error occurs
            if self.use_rich_logging:
                self.console.print(f"[red]Error parsing LLM response: {e}[/]")
                self.console.print(f"[yellow]Response: {response.content}[/]")
            
            preprocessed_query = PreprocessedQuery(
                original_query=query,
                reformulated_query=query,
                confidence=0.0
            )
            
            return preprocessed_query
    
    def _log_preprocessed_query(self, preprocessed_query: PreprocessedQuery) -> None:
        """
        Log the preprocessed query using rich formatting.
        
        Args:
            preprocessed_query: Preprocessed query
        """
        self.console.print(Panel(f"Preprocessed Query: {preprocessed_query.reformulated_query}", style="bold green"))
        
        if preprocessed_query.identified_domain:
            self.console.print(f"Identified Domain: [cyan]{preprocessed_query.identified_domain}[/]")
        
        if preprocessed_query.identified_fields:
            self.console.print(f"Identified Fields: [green]{', '.join(preprocessed_query.identified_fields)}[/]")
        
        if preprocessed_query.extraction_requirements:
            self.console.print("[bold]Extraction Requirements:[/]")
            for requirement, description in preprocessed_query.extraction_requirements.items():
                self.console.print(f"  [yellow]{requirement}:[/] {description}")
        
        self.console.print(f"Confidence: [magenta]{preprocessed_query.confidence:.2f}[/]")
