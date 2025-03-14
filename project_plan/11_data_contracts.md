# Data Contracts

## Business Description

Data Contracts define the structure and format of data exchanged between components in the extraction system. They provide a clear and consistent interface for data exchange, ensuring that components can interact reliably and predictably. These contracts are essential for maintaining system integrity, enabling component interoperability, and facilitating system evolution.

The Data Contracts are designed to:
- Define the structure of data exchanged between components
- Specify validation rules for data integrity
- Document the meaning and purpose of each data field
- Enable type checking and static analysis
- Support versioning and backward compatibility

## Dependencies

- **Configuration Service**: For contract configuration and validation settings
- **Error Handling Service**: For handling contract validation errors

## Core Contracts

### Input Contract

The Input Contract defines the structure of extraction requests sent to the system.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ExtractionRequest:
    """Request for document extraction."""
    
    document: str
    """The full text to process."""
    
    fields: List[str]
    """Fields to extract from the document."""
    
    domain: str
    """Domain context (e.g., "medical", "legal")."""
    
    output_formats: List[str] = field(default_factory=lambda: ["json", "text"])
    """Desired output formats."""
    
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    """Optional configuration overrides."""
    
    def validate(self) -> List[str]:
        """
        Validate the request.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.document:
            errors.append("Document is required")
            
        if not self.fields:
            errors.append("At least one field is required")
            
        if not self.domain:
            errors.append("Domain is required")
            
        # Check output formats
        valid_formats = ["json", "text", "xml"]
        for format in self.output_formats:
            if format not in valid_formats:
                errors.append(f"Invalid output format: {format}")
        
        return errors
```

### Output Contract

The Output Contract defines the structure of extraction results returned by the system.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ExtractionResult:
    """Result of document extraction."""
    
    json_output: Optional[Dict[str, Any]] = None
    """Structured JSON output."""
    
    text_output: Optional[str] = None
    """Flat text output."""
    
    xml_output: Optional[str] = None
    """XML output if requested."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Processing metadata including:
    - processing_time: float  # Total processing time
    - chunk_count: int  # Number of chunks processed
    - token_count: int  # Total tokens processed
    - warnings: List[str]  # Any warnings or issues
    """
    
    def has_output(self) -> bool:
        """
        Check if result has any output.
        
        Returns:
            True if result has any output
        """
        return (
            self.json_output is not None or
            self.text_output is not None or
            self.xml_output is not None
        )
    
    def has_errors(self) -> bool:
        """
        Check if result has errors.
        
        Returns:
            True if result has errors
        """
        return "error" in self.metadata
    
    def get_warnings(self) -> List[str]:
        """
        Get warnings from metadata.
        
        Returns:
            List of warnings
        """
        return self.metadata.get("warnings", [])
    
    def get_processing_time(self) -> float:
        """
        Get processing time from metadata.
        
        Returns:
            Processing time in seconds
        """
        return self.metadata.get("processing_time", 0.0)
```

### Field Definition Contract

The Field Definition Contract defines the structure of field definitions used for extraction.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class FieldDefinition:
    """Definition of a field to extract."""
    
    name: str
    """Field name."""
    
    description: str
    """Description for LLM context."""
    
    type: str = "string"
    """Field type (string, date, number, boolean, timeline)."""
    
    is_unique: bool = True
    """Whether field should have only one value."""
    
    validation_regex: Optional[str] = None
    """Optional validation pattern."""
    
    examples: List[str] = field(default_factory=list)
    """Example values for few-shot learning."""
    
    required: bool = False
    """Whether field is required."""
    
    date_format: Optional[str] = None
    """Format for date fields."""
    
    def validate(self) -> List[str]:
        """
        Validate the field definition.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.name:
            errors.append("Field name is required")
            
        if not self.description:
            errors.append("Field description is required")
            
        # Check field type
        valid_types = ["string", "date", "number", "boolean", "timeline"]
        if self.type not in valid_types:
            errors.append(f"Invalid field type: {self.type}")
            
        # Check regex if provided
        if self.validation_regex:
            try:
                import re
                re.compile(self.validation_regex)
            except re.error:
                errors.append(f"Invalid validation regex: {self.validation_regex}")
        
        return errors
```

### Document Chunk Contract

The Document Chunk Contract defines the structure of document chunks created by the chunker.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class DocumentChunk:
    """Chunk of a document."""
    
    text: str
    """The chunk text."""
    
    index: int
    """Chunk index in sequence."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Chunk metadata including:
    - start_position: int  # Character position in original document
    - end_position: int  # End character position
    - overlap_previous: bool  # Whether this chunk overlaps with previous
    - overlap_next: bool  # Whether this chunk overlaps with next
    - boundary_type: str  # Type of boundary used (e.g., "section", "paragraph")
    """
    
    def get_token_count(self) -> int:
        """
        Get token count from metadata.
        
        Returns:
            Token count or 0 if not available
        """
        return self.metadata.get("token_count", 0)
    
    def get_boundary_type(self) -> str:
        """
        Get boundary type from metadata.
        
        Returns:
            Boundary type or empty string if not available
        """
        return self.metadata.get("boundary_type", "")
    
    def has_overlap(self) -> bool:
        """
        Check if chunk has overlap.
        
        Returns:
            True if chunk overlaps with previous or next
        """
        return (
            self.metadata.get("overlap_previous", False) or
            self.metadata.get("overlap_next", False)
        )
```

### Extracted Fields Contract

The Extracted Fields Contract defines the structure of fields extracted from a chunk.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ExtractedFields:
    """Fields extracted from a chunk."""
    
    chunk_index: int
    """Index of chunk."""
    
    fields: Dict[str, Any]
    """Extracted field values."""
    
    confidence: Dict[str, float] = field(default_factory=dict)
    """Confidence scores per field."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""
    
    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """
        Get value of a field.
        
        Args:
            field_name: Name of the field
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        return self.fields.get(field_name, default)
    
    def get_confidence(self, field_name: str) -> float:
        """
        Get confidence score for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Confidence score (0.0-1.0) or 0.0 if not available
        """
        return self.confidence.get(field_name, 0.0)
    
    def has_field(self, field_name: str) -> bool:
        """
        Check if field is present.
        
        Args:
            field_name: Name of the field
            
        Returns:
            True if field is present
        """
        return field_name in self.fields
```

### Merged Result Contract

The Merged Result Contract defines the structure of merged extraction results.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class MergedResult:
    """Merged extraction results."""
    
    fields: Dict[str, Any]
    """Merged field values."""
    
    timeline: Optional[List[Dict[str, Any]]] = None
    """Timeline if applicable."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Merging metadata including:
    - source_chunks: Dict[str, List[int]]  # Mapping of fields to source chunks
    - conflicts: Dict[str, List[Any]]  # Fields with conflicting values
    - confidence: Dict[str, float]  # Confidence scores for merged fields
    """
    
    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """
        Get value of a field.
        
        Args:
            field_name: Name of the field
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        return self.fields.get(field_name, default)
    
    def get_source_chunks(self, field_name: str) -> List[int]:
        """
        Get source chunks for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            List of chunk indices or empty list if not available
        """
        return self.metadata.get("source_chunks", {}).get(field_name, [])
    
    def get_confidence(self, field_name: str) -> float:
        """
        Get confidence score for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Confidence score (0.0-1.0) or 0.0 if not available
        """
        return self.metadata.get("confidence", {}).get(field_name, 0.0)
    
    def has_conflicts(self, field_name: str) -> bool:
        """
        Check if field has conflicts.
        
        Args:
            field_name: Name of the field
            
        Returns:
            True if field has conflicts
        """
        return field_name in self.metadata.get("conflicts", {})
    
    def get_conflicts(self, field_name: str) -> List[Any]:
        """
        Get conflicts for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            List of conflicting values or empty list if not available
        """
        return self.metadata.get("conflicts", {}).get(field_name, [])
```

### Formatted Output Contract

The Formatted Output Contract defines the structure of formatted extraction results.

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class FormattedOutput:
    """Formatted extraction results."""
    
    json_output: Optional[Dict[str, Any]] = None
    """Structured JSON output."""
    
    text_output: Optional[str] = None
    """Flat text output."""
    
    xml_output: Optional[str] = None
    """XML output if requested."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Formatting metadata."""
    
    def has_format(self, format_name: str) -> bool:
        """
        Check if output has a specific format.
        
        Args:
            format_name: Name of the format
            
        Returns:
            True if format is available
        """
        if format_name == "json":
            return self.json_output is not None
        elif format_name == "text":
            return self.text_output is not None
        elif format_name == "xml":
            return self.xml_output is not None
        else:
            return False
    
    def get_output(self, format_name: str) -> Any:
        """
        Get output in a specific format.
        
        Args:
            format_name: Name of the format
            
        Returns:
            Output in the specified format or None if not available
        """
        if format_name == "json":
            return self.json_output
        elif format_name == "text":
            return self.text_output
        elif format_name == "xml":
            return self.xml_output
        else:
            return None
```

## Contract Validation

### ContractValidator

The ContractValidator is responsible for validating data against contracts.

```python
from typing import List, Dict, Any, Type, TypeVar, Generic

T = TypeVar('T')

class ContractValidator(Generic[T]):
    """Validator for data contracts."""
    
    def __init__(self, contract_class: Type[T]):
        """
        Initialize with contract class.
        
        Args:
            contract_class: Class of the contract
        """
        self.contract_class = contract_class
    
    def validate(self, data: Dict[str, Any]) -> Tuple[Optional[T], List[str]]:
        """
        Validate data against contract.
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (validated object, validation errors)
        """
        errors = []
        
        # Create object from data
        try:
            obj = self.contract_class(**data)
        except Exception as e:
            errors.append(f"Failed to create object: {str(e)}")
            return None, errors
        
        # Validate object if it has validate method
        if hasattr(obj, 'validate') and callable(getattr(obj, 'validate')):
            obj_errors = obj.validate()
            errors.extend(obj_errors)
        
        return obj, errors
```

## Features to Implement

1. **Contract Definition**
   - Define data structures for all components
   - Specify validation rules
   - Document field meanings and purposes
   - Support for complex nested structures

2. **Contract Validation**
   - Runtime validation of data
   - Type checking
   - Custom validation rules
   - Error reporting

3. **Contract Versioning**
   - Version tracking for contracts
   - Backward compatibility
   - Migration strategies
   - Deprecation handling

4. **Contract Documentation**
   - Automatic documentation generation
   - Example generation
   - Schema visualization
   - Usage guidelines

5. **Contract Testing**
   - Unit tests for contracts
   - Property-based testing
   - Fuzz testing
   - Compatibility testing

## Testing Strategy

### Unit Tests

1. **Contract Definition Tests**
   - Test contract class instantiation
   - Verify default values
   - Test field access methods
   - Verify metadata handling

2. **Validation Tests**
   - Test validation of valid data
   - Verify detection of invalid data
   - Test custom validation rules
   - Verify error messages

3. **Serialization Tests**
   - Test conversion to/from JSON
   - Verify handling of complex types
   - Test with different serialization formats
   - Verify round-trip conversion

### Integration Tests

1. **Component Integration Tests**
   - Test contracts with actual components
   - Verify data exchange between components
   - Test with real-world data
   - Verify error handling

2. **System Tests**
   - Test contracts in complete system
   - Verify end-to-end data flow
   - Test with different domains
   - Verify backward compatibility

### Property Tests

1. **Invariant Tests**
   - Test contract invariants
   - Verify properties that should always hold
   - Test with randomly generated data
   - Verify robustness against unexpected inputs

2. **Compatibility Tests**
   - Test compatibility between contract versions
   - Verify migration strategies
   - Test with historical data
   - Verify handling of deprecated fields

## Example Usage

```python
from typing import Dict, Any, List

def main():
    # Create extraction request
    request_data = {
        "document": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
        "fields": ["patient_name", "date_of_birth", "diagnosis"],
        "domain": "medical",
        "output_formats": ["json", "text"]
    }
    
    # Validate request
    request_validator = ContractValidator(ExtractionRequest)
    request, errors = request_validator.validate(request_data)
    
    if errors:
        print("Request validation errors:")
        for error in errors:
            print(f"- {error}")
        return
    
    # Process request (simplified)
    print(f"Processing document for domain: {request.domain}")
    print(f"Extracting fields: {', '.join(request.fields)}")
    
    # Create extraction result
    result_data = {
        "json_output": {
            "patient_name": "John Doe",
            "date_of_birth": "1980-05-15",
            "diagnosis": "Diabetes mellitus Type II"
        },
        "text_output": "patient_name: John Doe\ndate_of_birth: 1980-05-15\ndiagnosis: Diabetes mellitus Type II",
        "metadata": {
            "processing_time": 1.234,
            "chunk_count": 1,
            "token_count": 150
        }
    }
    
    # Validate result
    result_validator = ContractValidator(ExtractionResult)
    result, errors = result_validator.validate(result_data)
    
    if errors:
        print("Result validation errors:")
        for error in errors:
            print(f"- {error}")
        return
    
    # Use result
    print("\nExtraction Result:")
    print(f"Processing time: {result.get_processing_time():.2f} seconds")
    
    if result.json_output:
        print("\nJSON Output:")
        for field, value in result.json_output.items():
            print(f"- {field}: {value}")
    
    if result.text_output:
        print("\nText Output:")
        print(result.text_output)

# Run the function
main()
```

## Contract Evolution

As the system evolves, contracts will need to change to accommodate new features and requirements. The following guidelines should be followed to ensure smooth contract evolution:

1. **Backward Compatibility**
   - Add new fields with default values
   - Don't remove existing fields
   - Don't change field types
   - Don't change validation rules to be more restrictive

2. **Versioning**
   - Use semantic versioning for contracts
   - Increment major version for breaking changes
   - Increment minor version for backward-compatible additions
   - Increment patch version for bug fixes

3. **Deprecation**
   - Mark fields as deprecated before removal
   - Provide migration path for deprecated fields
   - Keep deprecated fields for at least one major version
   - Document deprecation in contract documentation

4. **Migration**
   - Provide migration tools for contract changes
   - Document migration steps
   - Test migration with real-world data
   - Support automatic migration when possible

By following these guidelines, the system can evolve while maintaining compatibility with existing components and data.
