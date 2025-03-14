"""
Example script demonstrating the use of the ConfigurationService in the Dudoxx Extraction system.

This script shows how to use the ConfigurationService to access configuration values
and create LLM and embedding models with the appropriate configuration.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dudoxx_extraction.configuration_service import ConfigurationService


def demonstrate_configuration_service():
    """Demonstrate the use of the ConfigurationService."""
    console = Console()
    
    # Create a configuration service
    console.print(Panel("Creating ConfigurationService", style="cyan"))
    config_service = ConfigurationService()
    
    # Display LLM configuration
    console.print(Panel("LLM Configuration", style="cyan"))
    llm_config = config_service.get_llm_config()
    
    llm_table = Table(title="LLM Configuration")
    llm_table.add_column("Setting", style="cyan")
    llm_table.add_column("Value", style="green")
    
    for key, value in llm_config.items():
        # Mask API key for security
        if key == "api_key" and value:
            masked_value = value[:4] + "..." + value[-4:]
            llm_table.add_row(key, masked_value)
        else:
            llm_table.add_row(key, str(value))
    
    console.print(llm_table)
    
    # Display embedding configuration
    console.print(Panel("Embedding Configuration", style="cyan"))
    embedding_config = config_service.get_embedding_config()
    
    embedding_table = Table(title="Embedding Configuration")
    embedding_table.add_column("Setting", style="cyan")
    embedding_table.add_column("Value", style="green")
    
    for key, value in embedding_config.items():
        # Mask API key for security
        if key == "api_key" and value:
            masked_value = value[:4] + "..." + value[-4:]
            embedding_table.add_row(key, masked_value)
        else:
            embedding_table.add_row(key, str(value))
    
    console.print(embedding_table)
    
    # Display extraction configuration
    console.print(Panel("Extraction Configuration", style="cyan"))
    extraction_config = config_service.get_extraction_config()
    
    extraction_table = Table(title="Extraction Configuration")
    extraction_table.add_column("Setting", style="cyan")
    extraction_table.add_column("Value", style="green")
    
    for key, value in extraction_config.items():
        extraction_table.add_row(key, str(value))
    
    console.print(extraction_table)
    
    # Create LLM and embedding models
    console.print(Panel("Creating LLM and Embedding Models", style="cyan"))
    
    try:
        # Create LLM
        llm = ChatOpenAI(
            base_url=llm_config["base_url"],
            api_key=llm_config["api_key"],
            model_name=llm_config["model_name"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"]
        )
        
        console.print(f"Created LLM: {llm.__class__.__name__}")
        console.print(f"Model: {llm_config['model_name']}")
        console.print(f"Base URL: {llm_config['base_url']}")
        
        # Create embeddings
        embeddings = OpenAIEmbeddings(
            base_url=embedding_config["base_url"],
            api_key=embedding_config["api_key"],
            model=embedding_config["model"]
        )
        
        console.print(f"Created Embeddings: {embeddings.__class__.__name__}")
        console.print(f"Model: {embedding_config['model']}")
        console.print(f"Base URL: {embedding_config['base_url']}")
        
    except Exception as e:
        console.print(f"Error creating models: {e}", style="red")
    
    # Validate configuration
    console.print(Panel("Validating Configuration", style="cyan"))
    is_valid = config_service.validate_config()
    
    if is_valid:
        console.print("Configuration is valid", style="green")
    else:
        console.print("Configuration is invalid", style="red")
    
    # Get specific configuration values
    console.print(Panel("Getting Specific Configuration Values", style="cyan"))
    
    model_name = config_service.get_config_value("llm", "model_name", "default-model")
    console.print(f"LLM Model Name: {model_name}")
    
    chunk_size = config_service.get_config_value("extraction", "chunk_size", 1000)
    console.print(f"Extraction Chunk Size: {chunk_size}")
    
    # Get non-existent configuration value
    non_existent = config_service.get_config_value("non_existent", "key", "default-value")
    console.print(f"Non-existent Value: {non_existent}")


if __name__ == "__main__":
    demonstrate_configuration_service()
