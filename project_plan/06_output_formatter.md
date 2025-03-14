# Output Formatter

## Business Description

The Output Formatter is responsible for generating structured outputs from the merged extraction results. This component takes the consolidated data from the Result Merger & Deduplicator and formats it into machine-readable JSON and human-friendly flat text formats. The JSON output is designed for programmatic access and database storage, while the flat text format is optimized for embedding models and vectorization.

The Output Formatter is designed to:
- Generate structured JSON with all extracted fields and metadata
- Create flat text representations for embedding models
- Support different output schemas based on domain requirements
- Include metadata for traceability and validation
- Format temporal data in a consistent and usable way

## Dependencies

- **Result Merger & Deduplicator**: Provides the merged extraction results
- **Temporal Normalizer**: Provides normalized temporal data
- **Configuration Service**: For output format settings
- **Logging Service**: For tracking formatting operations
- **Error Handling Service**: For managing exceptions during formatting

## Contracts

### Input
```python
class FormattingRequest:
    merged_result: MergedResult  # Merged extraction results
    output_formats: List[str] = ["json", "text"]  # Desired output formats
    include_metadata: bool = True  # Whether to include metadata
    domain: str  # Domain context (e.g., "medical", "legal")
```

### Output
```python
class FormattedOutput:
    json_output: Optional[Dict[str, Any]] = None  # Structured JSON output
    text_output: Optional[str] = None  # Flat text output
    metadata: Dict[str, Any]  # Formatting metadata
```

## Core Classes

### OutputFormatter (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format_output(self, merged_result: MergedResult, 
                     include_metadata: bool = True) -> Any:
        """
        Format merged result into output.
        
        Args:
            merged_result: Merged extraction results
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted output
        """
        pass
```

### Concrete Formatter Implementations

#### JSONFormatter
```python
import json
from typing import Dict, Any, Optional

class JSONFormatter(OutputFormatter):
    """Formats output as structured JSON."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize with optional schema.
        
        Args:
            schema: JSON schema for output
        """
        self.schema = schema
    
    def format_output(self, merged_result: MergedResult, 
                     include_metadata: bool = True) -> Dict[str, Any]:
        """
        Format merged result as JSON.
        
        Args:
            merged_result: Merged extraction results
            include_metadata: Whether to include metadata
            
        Returns:
            JSON-compatible dictionary
        """
        # Start with fields
        output = merged_result.fields.copy()
        
        # Add timeline if present
        if merged_result.timeline:
            output["Timeline"] = merged_result.timeline
        
        # Add metadata if requested
        if include_metadata:
            output["_metadata"] = {
                "source_chunks": merged_result.metadata.get("source_chunks", {}),
                "confidence": merged_result.metadata.get("confidence", {})
            }
            
            # Add conflicts if any
            conflicts = merged_result.metadata.get("conflicts", {})
            if conflicts:
                output["_metadata"]["conflicts"] = conflicts
        
        # Apply schema if provided
        if self.schema:
            output = self._apply_schema(output, self.schema)
        
        return output
    
    def _apply_schema(self, data: Dict[str, Any], 
                     schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply schema to data.
        
        Args:
            data: Data to format
            schema: Schema to apply
            
        Returns:
            Formatted data according to schema
        """
        # This is a simplified implementation
        # In a real implementation, this would validate against JSON Schema
        
        formatted = {}
        
        # Apply schema properties
        for key, prop in schema.get("properties", {}).items():
            if key in data:
                # Format based on type
                if prop.get("type") == "array" and isinstance(data[key], list):
                    if "items" in prop and prop["items"].get("type") == "object":
                        # Format array of objects
                        formatted[key] = [
                            self._apply_schema(item, prop["items"])
                            for item in data[key]
                        ]
                    else:
                        # Simple array
                        formatted[key] = data[key]
                elif prop.get("type") == "object" and isinstance(data[key], dict):
                    # Format nested object
                    formatted[key] = self._apply_schema(data[key], prop)
                else:
                    # Simple value
                    formatted[key] = data[key]
            elif key in schema.get("required", []):
                # Add null for required fields
                formatted[key] = None
        
        # Add fields not in schema
        for key, value in data.items():
            if key not in formatted and key not in schema.get("additionalProperties", {}):
                formatted[key] = value
        
        return formatted
```

#### FlatTextFormatter
```python
from typing import Dict, Any, List, Optional

class FlatTextFormatter(OutputFormatter):
    """Formats output as flat text for embeddings."""
    
    def __init__(self, field_order: Optional[List[str]] = None,
                include_field_names: bool = True):
        """
        Initialize with field order and options.
        
        Args:
            field_order: Order of fields in output
            include_field_names: Whether to include field names
        """
        self.field_order = field_order
        self.include_field_names = include_field_names
    
    def format_output(self, merged_result: MergedResult, 
                     include_metadata: bool = False) -> str:
        """
        Format merged result as flat text.
        
        Args:
            merged_result: Merged extraction results
            include_metadata: Whether to include metadata (ignored)
            
        Returns:
            Flat text representation
        """
        lines = []
        
        # Get fields in order
        fields = merged_result.fields
        field_names = self.field_order or sorted(fields.keys())
        
        # Add regular fields
        for field_name in field_names:
            if field_name not in fields:
                continue
                
            value = fields[field_name]
            
            if value is None:
                continue
                
            if isinstance(value, list):
                # Format list values
                if not value:
                    continue
                    
                if all(isinstance(item, dict) for item in value):
                    # List of objects (skip for flat text)
                    continue
                    
                if self.include_field_names:
                    for item in value:
                        lines.append(f"{field_name}: {item}")
                else:
                    lines.extend([str(item) for item in value])
            else:
                # Format single value
                if self.include_field_names:
                    lines.append(f"{field_name}: {value}")
                else:
                    lines.append(str(value))
        
        # Add timeline if present
        if merged_result.timeline:
            lines.append("")  # Empty line before timeline
            lines.append("Timeline:")
            
            for event in merged_result.timeline:
                date = event.get("date", "")
                
                # Get event description
                description = ""
                for key, value in event.items():
                    if key != "date":
                        if description:
                            description += ", "
                        description += f"{key}: {value}"
                
                lines.append(f"{date}: {description}")
        
        return "\n".join(lines)
```

#### XMLFormatter
```python
from typing import Dict, Any, Optional
import xml.dom.minidom as md
import xml.etree.ElementTree as ET

class XMLFormatter(OutputFormatter):
    """Formats output as XML."""
    
    def __init__(self, root_element: str = "Document",
                pretty_print: bool = True):
        """
        Initialize with XML options.
        
        Args:
            root_element: Name of root XML element
            pretty_print: Whether to format XML with indentation
        """
        self.root_element = root_element
        self.pretty_print = pretty_print
    
    def format_output(self, merged_result: MergedResult, 
                     include_metadata: bool = True) -> str:
        """
        Format merged result as XML.
        
        Args:
            merged_result: Merged extraction results
            include_metadata: Whether to include metadata
            
        Returns:
            XML string
        """
        # Create root element
        root = ET.Element(self.root_element)
        
        # Add fields
        fields_elem = ET.SubElement(root, "Fields")
        for field_name, value in merged_result.fields.items():
            self._add_element(fields_elem, field_name, value)
        
        # Add timeline if present
        if merged_result.timeline:
            timeline_elem = ET.SubElement(root, "Timeline")
            for event in merged_result.timeline:
                event_elem = ET.SubElement(timeline_elem, "Event")
                for key, value in event.items():
                    self._add_element(event_elem, key, value)
        
        # Add metadata if requested
        if include_metadata:
            metadata_elem = ET.SubElement(root, "Metadata")
            
            # Add source chunks
            sources_elem = ET.SubElement(metadata_elem, "SourceChunks")
            for field, chunks in merged_result.metadata.get("source_chunks", {}).items():
                field_elem = ET.SubElement(sources_elem, "Field", name=field)
                for chunk in chunks:
                    ET.SubElement(field_elem, "Chunk").text = str(chunk)
            
            # Add confidence scores
            confidence_elem = ET.SubElement(metadata_elem, "Confidence")
            for field, score in merged_result.metadata.get("confidence", {}).items():
                ET.SubElement(confidence_elem, "Field", name=field).text = str(score)
        
        # Convert to string
        xml_str = ET.tostring(root, encoding="unicode")
        
        # Pretty print if requested
        if self.pretty_print:
            xml_str = md.parseString(xml_str).toprettyxml(indent="  ")
        
        return xml_str
    
    def _add_element(self, parent: ET.Element, name: str, value: Any) -> None:
        """
        Add element to parent.
        
        Args:
            parent: Parent element
            name: Element name
            value: Element value
        """
        if value is None:
            ET.SubElement(parent, name, null="true")
        elif isinstance(value, list):
            list_elem = ET.SubElement(parent, name)
            
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    item_elem = ET.SubElement(list_elem, "Item", index=str(i))
                    for k, v in item.items():
                        self._add_element(item_elem, k, v)
                else:
                    ET.SubElement(list_elem, "Item").text = str(item)
        elif isinstance(value, dict):
            dict_elem = ET.SubElement(parent, name)
            for k, v in value.items():
                self._add_element(dict_elem, k, v)
        else:
            ET.SubElement(parent, name).text = str(value)
```

### OutputFormatterFactory
```python
from typing import Dict, Type, Optional

class OutputFormatterFactory:
    """Factory for creating output formatters."""
    
    def __init__(self):
        """Initialize with default formatters."""
        self.formatters = {
            "json": JSONFormatter,
            "text": FlatTextFormatter,
            "xml": XMLFormatter
        }
    
    def register_formatter(self, format_name: str, 
                          formatter_class: Type[OutputFormatter]) -> None:
        """
        Register a new formatter.
        
        Args:
            format_name: Name of the format
            formatter_class: Formatter class
        """
        self.formatters[format_name] = formatter_class
    
    def create_formatter(self, format_name: str, 
                        **kwargs) -> Optional[OutputFormatter]:
        """
        Create formatter for format.
        
        Args:
            format_name: Name of the format
            **kwargs: Additional arguments for formatter
            
        Returns:
            Formatter instance or None if format not supported
        """
        formatter_class = self.formatters.get(format_name)
        
        if formatter_class:
            return formatter_class(**kwargs)
            
        return None
```

### OutputManager
```python
from typing import Dict, Any, List, Optional

class OutputManager:
    """Manages output formatting."""
    
    def __init__(self, formatter_factory: OutputFormatterFactory):
        """
        Initialize with formatter factory.
        
        Args:
            formatter_factory: Factory for creating formatters
        """
        self.formatter_factory = formatter_factory
    
    def format_output(self, merged_result: MergedResult,
                     output_formats: List[str] = ["json", "text"],
                     include_metadata: bool = True,
                     formatter_options: Dict[str, Dict[str, Any]] = None) -> FormattedOutput:
        """
        Format merged result into requested formats.
        
        Args:
            merged_result: Merged extraction results
            output_formats: List of desired output formats
            include_metadata: Whether to include metadata
            formatter_options: Options for formatters
            
        Returns:
            Formatted output
        """
        formatter_options = formatter_options or {}
        json_output = None
        text_output = None
        xml_output = None
        
        # Format as JSON if requested
        if "json" in output_formats:
            json_formatter = self.formatter_factory.create_formatter(
                "json", **formatter_options.get("json", {})
            )
            
            if json_formatter:
                json_output = json_formatter.format_output(
                    merged_result, include_metadata
                )
        
        # Format as text if requested
        if "text" in output_formats:
            text_formatter = self.formatter_factory.create_formatter(
                "text", **formatter_options.get("text", {})
            )
            
            if text_formatter:
                text_output = text_formatter.format_output(
                    merged_result, False  # Never include metadata in text output
                )
        
        # Format as XML if requested
        if "xml" in output_formats:
            xml_formatter = self.formatter_factory.create_formatter(
                "xml", **formatter_options.get("xml", {})
            )
            
            if xml_formatter:
                xml_output = xml_formatter.format_output(
                    merged_result, include_metadata
                )
        
        return FormattedOutput(
            json_output=json_output,
            text_output=text_output,
            xml_output=xml_output,
            metadata={
                "formats": output_formats,
                "include_metadata": include_metadata
            }
        )
```

## Features to Implement

1. **JSON Output Generation**
   - Structured JSON with all extracted fields
   - Support for nested objects and arrays
   - Inclusion of metadata and confidence scores
   - Schema validation and enforcement

2. **Flat Text Generation**
   - Human-readable text format
   - Optimized for embedding models
   - Configurable field ordering and formatting
   - Timeline representation in narrative form

3. **XML Output Generation**
   - Structured XML with all extracted fields
   - Support for attributes and nested elements
   - Pretty printing and formatting options
   - XML schema validation

4. **Output Customization**
   - Domain-specific output formats
   - Configurable field inclusion/exclusion
   - Custom formatting rules per field
   - Template-based output generation

5. **Metadata Handling**
   - Inclusion of source information
   - Confidence scores for extracted fields
   - Processing statistics and metrics
   - Conflict and resolution information

## Testing Strategy

### Unit Tests

1. **Formatter Tests**
   - Test each formatter independently
   - Verify correct handling of different field types
   - Test metadata inclusion/exclusion
   - Verify output structure matches expectations

2. **Factory Tests**
   - Test formatter creation for different formats
   - Verify custom formatter registration
   - Test handling of unknown formats
   - Verify formatter options are passed correctly

3. **Edge Case Tests**
   - Test with empty or null values
   - Verify handling of complex nested structures
   - Test with very large datasets
   - Verify handling of special characters

### Integration Tests

1. **End-to-End Formatting Tests**
   - Test with real merged results
   - Verify correct formatting of different field types
   - Test with various document types
   - Measure formatting performance

2. **Domain-Specific Tests**
   - Test with medical records
   - Test with legal documents
   - Test with financial reports
   - Verify domain-specific formatting rules

### Validation Tests

1. **Schema Validation**
   - Verify JSON output matches expected schema
   - Test XML validation against XSD
   - Verify required fields are present
   - Test handling of invalid data

2. **Embedding Compatibility Tests**
   - Verify flat text format works with embedding models
   - Test vectorization of output
   - Measure semantic search performance
   - Verify information preservation

## Example Usage

```python
from typing import Dict, Any

def main():
    # Initialize factory
    formatter_factory = OutputFormatterFactory()
    
    # Register custom formatter if needed
    # formatter_factory.register_formatter("csv", CSVFormatter)
    
    # Initialize output manager
    output_manager = OutputManager(formatter_factory)
    
    # Sample merged result
    merged_result = MergedResult(
        fields={
            "patient_name": "John Doe",
            "date_of_birth": "1980-05-15",
            "diagnoses": ["Diabetes mellitus Type II", "Hypertension"],
            "medications": ["Metformin", "Lisinopril"]
        },
        timeline=[
            {
                "date": "2021-07-10",
                "description": "Patient reported dizziness, medication X prescribed."
            },
            {
                "date": "2021-08-20",
                "description": "Follow-up visit, blood sugar levels improved."
            }
        ],
        metadata={
            "source_chunks": {
                "patient_name": [0, 1],
                "date_of_birth": [0],
                "diagnoses": [0, 2],
                "medications": [1, 2]
            },
            "confidence": {
                "patient_name": 0.9,
                "date_of_birth": 0.8,
                "diagnoses": 0.8,
                "medications": 0.9
            }
        }
    )
    
    # Formatter options
    formatter_options = {
        "json": {
            "schema": {
                "properties": {
                    "patient_name": {"type": "string"},
                    "date_of_birth": {"type": "string"},
                    "diagnoses": {"type": "array", "items": {"type": "string"}},
                    "medications": {"type": "array", "items": {"type": "string"}},
                    "Timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "text": {
            "field_order": ["patient_name", "date_of_birth", "diagnoses", "medications"],
            "include_field_names": True
        },
        "xml": {
            "root_element": "MedicalRecord",
            "pretty_print": True
        }
    }
    
    # Format output
    formatted_output = output_manager.format_output(
        merged_result=merged_result,
        output_formats=["json", "text", "xml"],
        include_metadata=True,
        formatter_options=formatter_options
    )
    
    # Print JSON output
    if formatted_output.json_output:
        print("JSON Output:")
        print(json.dumps(formatted_output.json_output, indent=2))
        print()
    
    # Print text output
    if formatted_output.text_output:
        print("Text Output:")
        print(formatted_output.text_output)
        print()
    
    # Print XML output
    if formatted_output.xml_output:
        print("XML Output:")
        print(formatted_output.xml_output)

# Run the function
main()
