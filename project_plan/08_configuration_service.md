# Configuration Service

## Business Description

The Configuration Service is responsible for managing all configuration settings for the extraction system. It provides a centralized way to define, access, and validate configuration parameters for all components of the pipeline. This service enables domain-specific customization, component-specific settings, and runtime configuration overrides, making the system adaptable to different document types and extraction requirements.

The Configuration Service is designed to:
- Provide a centralized repository for all configuration settings
- Support domain-specific configurations for different document types
- Enable component-specific settings for fine-grained control
- Validate configuration parameters to ensure system integrity
- Allow runtime configuration overrides for flexibility

## Dependencies

- **Logging Service**: For tracking configuration operations
- **Error Handling Service**: For managing exceptions during configuration loading and validation

## Contracts

### Input
```python
class ConfigurationRequest:
    domain: Optional[str] = None  # Domain for domain-specific configuration
    component: Optional[str] = None  # Component for component-specific configuration
    key: Optional[str] = None  # Specific configuration key
    default: Any = None  # Default value if configuration not found
```

### Output
```python
class ConfigurationResult:
    value: Any  # Configuration value
    source: str  # Source of configuration (e.g., "global", "domain", "component")
    metadata: Dict[str, Any]  # Additional metadata
```

## Core Classes

### ConfigurationProvider (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ConfigurationProvider(ABC):
    """Abstract base class for configuration providers."""
    
    @abstractmethod
    def get_configuration(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration.
        
        Args:
            key: Optional key for specific configuration
            
        Returns:
            Configuration dictionary
        """
        pass
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validated configuration
        """
        pass
```

### Concrete Provider Implementations

#### FileConfigurationProvider
```python
import os
import json
import yaml
from typing import Dict, Any, Optional

class FileConfigurationProvider(ConfigurationProvider):
    """Provides configuration from files."""
    
    def __init__(self, config_dir: str, file_format: str = "json"):
        """
        Initialize with configuration directory.
        
        Args:
            config_dir: Directory containing configuration files
            file_format: Format of configuration files (json or yaml)
        """
        self.config_dir = config_dir
        self.file_format = file_format
        self.config_cache = {}
    
    def get_configuration(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration from file.
        
        Args:
            key: Optional key for specific configuration file
            
        Returns:
            Configuration dictionary
        """
        # Determine file path
        if key:
            file_name = f"{key}.{self.file_format}"
        else:
            file_name = f"config.{self.file_format}"
            
        file_path = os.path.join(self.config_dir, file_name)
        
        # Check cache
        if file_path in self.config_cache:
            return self.config_cache[file_path]
            
        # Load configuration
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, "r") as f:
                if self.file_format == "json":
                    config = json.load(f)
                elif self.file_format == "yaml":
                    config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {self.file_format}")
                    
            # Validate configuration
            config = self.validate_configuration(config)
            
            # Cache configuration
            self.config_cache[file_path] = config
            
            return config
        except Exception as e:
            # Return empty configuration on error
            return {}
    
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validated configuration
        """
        # Simple validation
        if not isinstance(config, dict):
            return {}
            
        return config
```

#### EnvironmentConfigurationProvider
```python
import os
import json
from typing import Dict, Any, Optional

class EnvironmentConfigurationProvider(ConfigurationProvider):
    """Provides configuration from environment variables."""
    
    def __init__(self, prefix: str = "EXTRACTION_"):
        """
        Initialize with environment variable prefix.
        
        Args:
            prefix: Prefix for environment variables
        """
        self.prefix = prefix
    
    def get_configuration(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration from environment variables.
        
        Args:
            key: Optional key for specific configuration
            
        Returns:
            Configuration dictionary
        """
        config = {}
        
        # Get all environment variables with prefix
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(self.prefix):
                continue
                
            # Remove prefix
            config_key = env_key[len(self.prefix):].lower()
            
            # Filter by key if provided
            if key and not config_key.startswith(key.lower()):
                continue
                
            # Parse value
            try:
                # Try to parse as JSON
                config[config_key] = json.loads(env_value)
            except json.JSONDecodeError:
                # Use as string
                config[config_key] = env_value
        
        # Validate configuration
        return self.validate_configuration(config)
    
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validated configuration
        """
        # Simple validation
        if not isinstance(config, dict):
            return {}
            
        return config
```

#### DefaultConfigurationProvider
```python
from typing import Dict, Any, Optional

class DefaultConfigurationProvider(ConfigurationProvider):
    """Provides default configuration values."""
    
    def __init__(self, defaults: Dict[str, Any]):
        """
        Initialize with default values.
        
        Args:
            defaults: Default configuration values
        """
        self.defaults = defaults
    
    def get_configuration(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Args:
            key: Optional key for specific configuration
            
        Returns:
            Configuration dictionary
        """
        if key:
            # Return specific section
            return {k: v for k, v in self.defaults.items() if k.startswith(key)}
        else:
            # Return all defaults
            return self.defaults
    
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validated configuration
        """
        # No validation for defaults
        return config
```

### ConfigurationService
```python
from typing import Dict, Any, List, Optional
import copy

class ConfigurationService:
    """Service for managing configuration."""
    
    def __init__(self, providers: List[ConfigurationProvider],
                logger: LoggingService,
                error_handler: ErrorHandlingService):
        """
        Initialize with providers and services.
        
        Args:
            providers: List of configuration providers
            logger: For logging
            error_handler: For error handling
        """
        self.providers = providers
        self.logger = logger
        self.error_handler = error_handler
        
        # Cache for configurations
        self.global_config = None
        self.domain_configs = {}
        self.component_configs = {}
    
    def get_global_config(self) -> Dict[str, Any]:
        """
        Get global configuration.
        
        Returns:
            Global configuration dictionary
        """
        if self.global_config is None:
            # Load global configuration
            self.global_config = {}
            
            for provider in self.providers:
                try:
                    provider_config = provider.get_configuration()
                    self.global_config = self._merge_configs(
                        self.global_config, provider_config
                    )
                except Exception as e:
                    self.error_handler.handle_configuration_error(e, "global")
            
            # Log configuration loaded
            self.logger.log_info(
                "Global configuration loaded",
                {"provider_count": len(self.providers)}
            )
        
        return copy.deepcopy(self.global_config)
    
    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        """
        Get domain-specific configuration.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain-specific configuration dictionary
        """
        if domain not in self.domain_configs:
            # Load domain configuration
            domain_config = self.get_global_config()
            
            for provider in self.providers:
                try:
                    provider_config = provider.get_configuration(f"domains/{domain}")
                    domain_config = self._merge_configs(
                        domain_config, provider_config
                    )
                except Exception as e:
                    self.error_handler.handle_configuration_error(e, f"domain:{domain}")
            
            # Add domain name
            domain_config["name"] = domain
            
            # Cache domain configuration
            self.domain_configs[domain] = domain_config
            
            # Log configuration loaded
            self.logger.log_info(
                f"Domain configuration loaded: {domain}",
                {"domain": domain}
            )
        
        return copy.deepcopy(self.domain_configs[domain])
    
    def get_component_config(self, component: str, 
                           domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get component-specific configuration.
        
        Args:
            component: Component name
            domain: Optional domain name
            
        Returns:
            Component-specific configuration dictionary
        """
        cache_key = f"{component}:{domain}" if domain else component
        
        if cache_key not in self.component_configs:
            # Start with global or domain configuration
            if domain:
                base_config = self.get_domain_config(domain)
            else:
                base_config = self.get_global_config()
            
            # Get component section from base config
            component_config = base_config.get(component, {})
            
            # Load component-specific configuration
            for provider in self.providers:
                try:
                    provider_path = f"components/{component}"
                    if domain:
                        provider_path = f"domains/{domain}/{provider_path}"
                        
                    provider_config = provider.get_configuration(provider_path)
                    component_config = self._merge_configs(
                        component_config, provider_config
                    )
                except Exception as e:
                    self.error_handler.handle_configuration_error(
                        e, f"component:{component}:{domain}"
                    )
            
            # Cache component configuration
            self.component_configs[cache_key] = component_config
            
            # Log configuration loaded
            self.logger.log_info(
                f"Component configuration loaded: {component}",
                {"component": component, "domain": domain}
            )
        
        return copy.deepcopy(self.component_configs[cache_key])
    
    def get_field_definitions(self, domain: str, 
                            field_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get field definitions for domain.
        
        Args:
            domain: Domain name
            field_names: Optional list of field names to filter
            
        Returns:
            List of field definitions
        """
        # Get domain configuration
        domain_config = self.get_domain_config(domain)
        
        # Get field definitions
        all_fields = domain_config.get("fields", [])
        
        if not field_names:
            return copy.deepcopy(all_fields)
            
        # Filter by field names
        fields = []
        for field in all_fields:
            if field.get("name") in field_names:
                fields.append(field)
        
        return copy.deepcopy(fields)
    
    def get_config_value(self, key: str, default: Any = None,
                       domain: Optional[str] = None,
                       component: Optional[str] = None) -> Any:
        """
        Get specific configuration value.
        
        Args:
            key: Configuration key (dot notation)
            default: Default value if not found
            domain: Optional domain name
            component: Optional component name
            
        Returns:
            Configuration value
        """
        # Get configuration
        if component:
            config = self.get_component_config(component, domain)
        elif domain:
            config = self.get_domain_config(domain)
        else:
            config = self.get_global_config()
        
        # Split key into parts
        parts = key.split(".")
        
        # Navigate through config
        value = config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def _merge_configs(self, base: Dict[str, Any], 
                      override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration dictionaries.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if (key in result and isinstance(result[key], dict) 
                    and isinstance(value, dict)):
                # Recursively merge dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Override value
                result[key] = copy.deepcopy(value)
        
        return result
```

### ConfigurationValidator
```python
import jsonschema
from typing import Dict, Any, Optional

class ConfigurationValidator:
    """Validates configuration against schemas."""
    
    def __init__(self, schema_provider: ConfigurationProvider):
        """
        Initialize with schema provider.
        
        Args:
            schema_provider: Provider for validation schemas
        """
        self.schema_provider = schema_provider
        self.schema_cache = {}
    
    def validate_config(self, config: Dict[str, Any], 
                       schema_key: str) -> Dict[str, Any]:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration to validate
            schema_key: Key for schema
            
        Returns:
            Validated configuration
            
        Raises:
            ValidationError: If configuration is invalid
        """
        # Get schema
        schema = self._get_schema(schema_key)
        
        if not schema:
            # No schema, return as is
            return config
            
        # Validate configuration
        jsonschema.validate(config, schema)
        
        return config
    
    def _get_schema(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for key.
        
        Args:
            key: Schema key
            
        Returns:
            Schema dictionary or None if not found
        """
        if key in self.schema_cache:
            return self.schema_cache[key]
            
        # Load schema
        schema = self.schema_provider.get_configuration(f"schemas/{key}")
        
        # Cache schema
        self.schema_cache[key] = schema
        
        return schema
```

## Features to Implement

1. **Configuration Hierarchy**
   - Global default configuration
   - Domain-specific configuration
   - Component-specific configuration
   - Runtime configuration overrides

2. **Multiple Configuration Sources**
   - File-based configuration (JSON, YAML)
   - Environment variables
   - Command-line arguments
   - Database-stored configuration

3. **Configuration Validation**
   - Schema-based validation
   - Type checking
   - Required field validation
   - Cross-field validation

4. **Dynamic Configuration**
   - Hot reloading of configuration
   - Configuration change notifications
   - Configuration versioning
   - Configuration history

5. **Configuration Management**
   - Configuration backup and restore
   - Configuration export and import
   - Configuration documentation generation
   - Configuration UI for administration

## Testing Strategy

### Unit Tests

1. **Provider Tests**
   - Test each provider independently
   - Verify correct loading of configuration
   - Test handling of missing files/variables
   - Verify validation logic

2. **Service Tests**
   - Test configuration hierarchy
   - Verify merging of configurations
   - Test caching behavior
   - Verify error handling

3. **Validator Tests**
   - Test schema validation
   - Verify handling of invalid configurations
   - Test complex validation rules
   - Verify error messages

### Integration Tests

1. **Component Integration Tests**
   - Test configuration service with other components
   - Verify correct configuration application
   - Test with different domains
   - Verify component-specific settings

2. **System Tests**
   - Test configuration in complete system
   - Verify configuration changes affect behavior
   - Test with different deployment environments
   - Verify configuration documentation

### Performance Tests

1. **Loading Performance**
   - Measure configuration loading time
   - Test with large configuration files
   - Verify caching effectiveness
   - Measure memory usage

2. **Access Performance**
   - Measure configuration access time
   - Test with frequent configuration access
   - Verify performance with deep configuration hierarchies
   - Test concurrent access

## Example Usage

```python
from typing import Dict, Any

def main():
    # Initialize providers
    file_provider = FileConfigurationProvider("config/", "json")
    env_provider = EnvironmentConfigurationProvider("EXTRACTION_")
    default_provider = DefaultConfigurationProvider({
        "chunking": {
            "max_chunk_size": 16000,
            "overlap_size": 200
        },
        "processing": {
            "max_concurrency": 20,
            "retry_attempts": 3
        }
    })
    
    # Initialize services
    logger = LoggingService()
    error_handler = ErrorHandlingService(logger)
    
    # Initialize configuration service
    config_service = ConfigurationService(
        providers=[default_provider, file_provider, env_provider],
        logger=logger,
        error_handler=error_handler
    )
    
    # Get global configuration
    global_config = config_service.get_global_config()
    print("Global Configuration:")
    print(f"- Max Chunk Size: {global_config['chunking']['max_chunk_size']}")
    print(f"- Max Concurrency: {global_config['processing']['max_concurrency']}")
    
    # Get domain-specific configuration
    medical_config = config_service.get_domain_config("medical")
    print("\nMedical Domain Configuration:")
    print(f"- Max Chunk Size: {medical_config['chunking']['max_chunk_size']}")
    
    # Get component-specific configuration
    chunker_config = config_service.get_component_config("chunking", "medical")
    print("\nChunker Configuration for Medical Domain:")
    print(f"- Max Chunk Size: {chunker_config['max_chunk_size']}")
    
    # Get field definitions
    fields = config_service.get_field_definitions(
        "medical", ["patient_name", "date_of_birth"]
    )
    print("\nMedical Field Definitions:")
    for field in fields:
        print(f"- {field['name']}: {field['description']}")
    
    # Get specific configuration value
    retry_attempts = config_service.get_config_value(
        "processing.retry_attempts", default=3
    )
    print(f"\nRetry Attempts: {retry_attempts}")

# Run the function
main()
```

## Example Configuration Files

### Global Configuration (config/config.json)
```json
{
  "chunking": {
    "max_chunk_size": 16000,
    "overlap_size": 200,
    "default_strategy": "paragraph"
  },
  "processing": {
    "max_concurrency": 20,
    "retry_attempts": 3,
    "timeout": 60
  },
  "extraction": {
    "model_name": "dudoxx-extract-1",
    "temperature": 0.0
  },
  "normalization": {
    "date_format": "%Y-%m-%d"
  },
  "merging": {
    "deduplication_threshold": 0.9
  },
  "formatting": {
    "include_metadata": true,
    "default_formats": ["json", "text"]
  }
}
```

### Domain Configuration (config/domains/medical.json)
```json
{
  "chunking": {
    "default_strategy": "section"
  },
  "fields": [
    {
      "name": "patient_name",
      "description": "Full name of the patient",
      "type": "string",
      "is_unique": true
    },
    {
      "name": "date_of_birth",
      "description": "Patient's date of birth in YYYY-MM-DD format",
      "type": "date",
      "validation_regex": "^\\d{4}-\\d{2}-\\d{2}$",
      "is_unique": true
    },
    {
      "name": "diagnoses",
      "description": "Medical diagnoses",
      "type": "string",
      "is_unique": false
    },
    {
      "name": "medications",
      "description": "Prescribed medications",
      "type": "string",
      "is_unique": false
    },
    {
      "name": "visits",
      "description": "Medical visits",
      "type": "timeline",
      "date_field": "date",
      "is_unique": false
    }
  ],
  "timeline": {
    "events_field": "visits",
    "date_field": "date",
    "event_fields": ["description", "treatment"],
    "sort_ascending": true,
    "merge_same_day": true
  }
}
```

### Component Configuration (config/components/chunking.json)
```json
{
  "strategies": {
    "paragraph": {
      "separator_patterns": [
        "\\n\\s*\\n",
        "\\n\\s*\\-{3,}\\s*\\n"
      ]
    },
    "section": {
      "heading_patterns": [
        "^#+\\s+.+$",
        "^(?:Section|Chapter|Part)\\s+\\d+",
        "^[A-Z][^.!?]*[.!?]$"
      ]
    }
  },
  "token_counter": {
    "model_name": "gpt-3.5-turbo",
    "fallback_ratio": 1.3
  }
}
