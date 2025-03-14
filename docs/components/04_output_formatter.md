# Output Formatter

The `OutputFormatter` is a versatile component in the Dudoxx Extraction system that handles the formatting of extraction results into various output formats.

## Overview

After the extraction pipeline has processed a document and merged the results, the `OutputFormatter` takes the merged result and formats it into the requested output formats. This component supports multiple output formats, including JSON, text, and XML, allowing users to choose the format that best suits their needs.

## Key Features

1. **Multiple Output Formats**: Supports JSON, text, and XML output formats
2. **Metadata Handling**: Controls the inclusion of metadata in the output
3. **Hierarchical Data Formatting**: Handles complex nested data structures
4. **Pretty Printing**: Formats the output for readability
5. **Customizable Formatting**: Allows for customization of the output format

## Implementation

The `OutputFormatter` class is implemented in the extraction pipeline. Here's a simplified version of the class:

```python
class OutputFormatter:
    def __init__(self, logger=None):
        self.logger = logger
    
    def format_json(self, merged_result, include_metadata=True):
        if self.logger:
            self.logger.log_step("Output Formatting", "Formatting output as JSON")
            
        result = merged_result.copy()
        
        if not include_metadata:
            # Remove metadata fields
            keys_to_remove = [key for key in result if key.startswith("_")]
            for key in keys_to_remove:
                del result[key]
        
        return result
    
    def format_text(self, merged_result):
        if self.logger:
            self.logger.log_step("Output Formatting", "Formatting output as text")
            
        lines = []
        
        # Add regular fields
        for field_name, value in merged_result.items():
            if field_name.startswith("_"):
                # Skip metadata fields
                continue
                
            if isinstance(value, list):
                # Format list values
                for item in value:
                    if isinstance(item, dict):
                        # Format dictionary items
                        item_str = ", ".join([f"{k}: {v}" for k, v in item.items()])
                        lines.append(f"{field_name}: {item_str}")
                    else:
                        # Format simple items
                        lines.append(f"{field_name}: {item}")
            elif isinstance(value, dict):
                # Format dictionary values
                for k, v in value.items():
                    lines.append(f"{field_name}.{k}: {v}")
            else:
                # Format single value
                lines.append(f"{field_name}: {value}")
        
        # Add timeline if present
        if "timeline" in merged_result:
            lines.append("")  # Empty line before timeline
            lines.append("Timeline:")
            
            for event in merged_result["timeline"]:
                date = event.get("date", "")
                description = event.get("description", "")
                lines.append(f"{date}: {description}")
        
        return "\n".join(lines)
    
    def format_xml(self, merged_result):
        if self.logger:
            self.logger.log_step("Output Formatting", "Formatting output as XML")
            
        import xml.dom.minidom as md
        import xml.etree.ElementTree as ET
        
        # Create root element
        root = ET.Element("Document")
        
        # Add fields
        fields_elem = ET.SubElement(root, "Fields")
        for field_name, value in merged_result.items():
            if field_name.startswith("_"):
                # Skip metadata fields
                continue
                
            self._add_xml_element(fields_elem, field_name, value)
        
        # Add metadata if present
        if "_metadata" in merged_result:
            metadata_elem = ET.SubElement(root, "Metadata")
            for key, value in merged_result["_metadata"].items():
                self._add_xml_element(metadata_elem, key, value)
        
        # Convert to string and pretty print
        xml_str = ET.tostring(root, encoding="unicode")
        pretty_xml = md.parseString(xml_str).toprettyxml(indent="  ")
        
        return pretty_xml
    
    def _add_xml_element(self, parent, name, value):
        import xml.etree.ElementTree as ET
        
        if value is None:
            ET.SubElement(parent, name, null="true")
        elif isinstance(value, list):
            list_elem = ET.SubElement(parent, name)
            
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    item_elem = ET.SubElement(list_elem, "Item", index=str(i))
                    for k, v in item.items():
                        self._add_xml_element(item_elem, k, v)
                else:
                    ET.SubElement(list_elem, "Item").text = str(item)
        elif isinstance(value, dict):
            dict_elem = ET.SubElement(parent, name)
            for k, v in value.items():
                self._add_xml_element(dict_elem, k, v)
        else:
            ET.SubElement(parent, name).text = str(value)
```

## Formatting Process

### JSON Formatting

1. **Copy**: Create a copy of the merged result to avoid modifying the original.
2. **Metadata Handling**: Optionally remove metadata fields (those starting with "_").
3. **Return**: Return the formatted JSON result.

### Text Formatting

1. **Initialization**: Create an empty list to store the formatted lines.
2. **Field Formatting**: Format each field based on its type:
   - For list fields, format each item in the list.
   - For dictionary fields, format each key-value pair.
   - For simple fields, format the field name and value.
3. **Timeline Handling**: If a timeline is present, add it to the formatted output.
4. **Join**: Join all lines with newline characters and return the result.

### XML Formatting

1. **Root Element**: Create a root XML element.
2. **Field Elements**: Add each field as a child element of the root element.
3. **Metadata Elements**: Add metadata as a separate section if present.
4. **Pretty Print**: Convert the XML to a string and pretty print it for readability.
5. **Return**: Return the formatted XML result.

## Usage Example

```python
# Initialize components
logger = RichLogger(verbose=True)

# Create output formatter
formatter = OutputFormatter(logger=logger)

# Format result as JSON
json_output = formatter.format_json(merged_result, include_metadata=True)
print(json.dumps(json_output, indent=2))

# Format result as text
text_output = formatter.format_text(merged_result)
print(text_output)

# Format result as XML
xml_output = formatter.format_xml(merged_result)
print(xml_output)
```

## Integration with Extraction Pipeline

The `OutputFormatter` is integrated into the extraction pipeline and is used to format the final output:

```python
# In ExtractionPipeline.process_document
# Step 6: Format output
output = {}
if "json" in output_formats:
    output["json_output"] = self.output_formatter.format_json(merged_result)
    
if "text" in output_formats:
    output["text_output"] = self.output_formatter.format_text(merged_result)
    
if "xml" in output_formats:
    output["xml_output"] = self.output_formatter.format_xml(merged_result)
```

## Benefits

1. **Flexibility**: Supports multiple output formats to meet different needs.
2. **Readability**: Formats the output for human readability.
3. **Metadata Control**: Allows control over the inclusion of metadata.
4. **Hierarchical Data Support**: Handles complex nested data structures.
5. **Customizability**: Can be extended to support additional output formats.

## Customization

The `OutputFormatter` can be customized in several ways:

1. **Output Formats**: Add support for additional output formats (e.g., CSV, YAML).
2. **Formatting Options**: Add options to control the formatting of specific fields.
3. **Metadata Handling**: Customize the handling of metadata fields.
4. **Pretty Printing**: Adjust the pretty printing settings for better readability.
5. **Field Naming**: Customize the naming of fields in the output.

## Example Output

### JSON Output

```json
{
  "patient_name": "John Smith",
  "date_of_birth": "1980-05-15",
  "diagnoses": [
    "Type 2 Diabetes",
    "Hypertension",
    "Upper respiratory infection"
  ],
  "medications": [
    "Metformin 500mg twice daily (for diabetes)",
    "Lisinopril 10mg once daily (for hypertension)",
    "Aspirin 81mg once daily (preventative)"
  ],
  "visits": [
    {
      "date": "2023-03-10",
      "description": "Upper respiratory infection, likely viral"
    },
    {
      "date": "2023-07-22",
      "description": "Type 2 Diabetes - well controlled"
    },
    {
      "date": "2023-11-15",
      "description": "Overall good health, mild hyperlipidemia"
    }
  ],
  "_metadata": {
    "source_chunks": {
      "patient_name": [0],
      "date_of_birth": [0],
      "diagnoses": [0],
      "medications": [0],
      "visits": [0]
    },
    "confidence": {
      "patient_name": [1.0],
      "date_of_birth": [1.0],
      "diagnoses": [1.0],
      "medications": [1.0],
      "visits": [1.0]
    }
  }
}
```

### Text Output

```
patient_name: John Smith
date_of_birth: 1980-05-15
diagnoses: Type 2 Diabetes
diagnoses: Hypertension
diagnoses: Upper respiratory infection
medications: Metformin 500mg twice daily (for diabetes)
medications: Lisinopril 10mg once daily (for hypertension)
medications: Aspirin 81mg once daily (preventative)
visits: date: 2023-03-10, description: Upper respiratory infection, likely viral
visits: date: 2023-07-22, description: Type 2 Diabetes - well controlled
visits: date: 2023-11-15, description: Overall good health, mild hyperlipidemia
```

### XML Output

```xml
<?xml version="1.0" ?>
<Document>
  <Fields>
    <patient_name>John Smith</patient_name>
    <date_of_birth>1980-05-15</date_of_birth>
    <diagnoses>
      <Item>Type 2 Diabetes</Item>
      <Item>Hypertension</Item>
      <Item>Upper respiratory infection</Item>
    </diagnoses>
    <medications>
      <Item>Metformin 500mg twice daily (for diabetes)</Item>
      <Item>Lisinopril 10mg once daily (for hypertension)</Item>
      <Item>Aspirin 81mg once daily (preventative)</Item>
    </medications>
    <visits>
      <Item index="0">
        <date>2023-03-10</date>
        <description>Upper respiratory infection, likely viral</description>
      </Item>
      <Item index="1">
        <date>2023-07-22</date>
        <description>Type 2 Diabetes - well controlled</description>
      </Item>
      <Item index="2">
        <date>2023-11-15</date>
        <description>Overall good health, mild hyperlipidemia</description>
      </Item>
    </visits>
  </Fields>
  <Metadata>
    <source_chunks>
      <patient_name>
        <Item>0</Item>
      </patient_name>
      <date_of_birth>
        <Item>0</Item>
      </date_of_birth>
      <diagnoses>
        <Item>0</Item>
      </diagnoses>
      <medications>
        <Item>0</Item>
      </medications>
      <visits>
        <Item>0</Item>
      </visits>
    </source_chunks>
    <confidence>
      <patient_name>
        <Item>1.0</Item>
      </patient_name>
      <date_of_birth>
        <Item>1.0</Item>
      </date_of_birth>
      <diagnoses>
        <Item>1.0</Item>
      </diagnoses>
      <medications>
        <Item>1.0</Item>
      </medications>
      <visits>
        <Item>1.0</Item>
      </visits>
    </confidence>
  </Metadata>
</Document>
