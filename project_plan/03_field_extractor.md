# Field Extractor

## Business Description

The Field Extractor is responsible for extracting specified fields from each document chunk using dynamic prompts. This component is guided by a provided field list that can vary by domain or document type. The prompt given to Dudoxx's LLM for each chunk dynamically includes these target fields, instructing the model to identify and extract the corresponding values from the text.

The Field Extractor is designed to:
- Construct domain-specific prompts with field lists
- Support few-shot examples for complex domains
- Parse and validate LLM responses
- Handle different output formats (primarily JSON)
- Adapt to different domains without code changes

## Dependencies

- **Parallel LLM Processor**: For sending prompts to the LLM
- **Configuration Service**: For domain-specific field definitions and prompt templates
- **Logging Service**: For tracking extraction operations and potential issues
- **Error Handling Service**: For managing exceptions during extraction

## Contracts

### Input
```python
class ExtractionRequest:
    chunk: DocumentChunk  # Chunk to extract fields from
    fields: List[str]  # Fields to extract
    domain: str  # Domain context (e.g., "medical", "legal")
    examples: Optional[List[Dict[str, Any]]] = None  # Few-shot examples
    output_format: str = "json"  # Desired output format
```

### Output
```python
class ExtractedFields:
    chunk_index: int  # Index of chunk
    fields: Dict[str, Any]  # Extracted field values
    confidence: Dict[str, float]  # Confidence scores per field
    metadata: Dict[str, Any]  # Additional metadata
```

## Core Classes

### PromptBuilder
```python
from typing import List, Dict, Any, Optional
import json

class PromptBuilder:
    """Builds prompts for field extraction."""
    
    def __init__(self, prompt_templates: Dict[str, str] = None):
        """
        Initialize with optional prompt templates.
        
        Args:
            prompt_templates: Domain-specific prompt templates
        """
        self.default_template = """
        Extract the following fields from the text:
        {field_descriptions}
        
        Return the extracted information in JSON format with the following structure:
        {json_structure}
        
        If a field is not present in the text, set its value to null.
        
        Text:
        {text}
        """
        
        self.prompt_templates = prompt_templates or {}
    
    def build_extraction_prompt(self, chunk_text: str, 
                               fields: List[Dict[str, str]], 
                               domain: str = None, 
                               examples: List[Dict[str, Any]] = None) -> str:
        """
        Build prompt for field extraction.
        
        Args:
            chunk_text: Text to extract fields from
            fields: List of field definitions (name, description)
            domain: Domain context
            examples: Few-shot examples
            
        Returns:
            Formatted prompt
        """
        template = self.prompt_templates.get(domain, self.default_template)
        
        # Format field descriptions
        field_descriptions = "\n".join([
            f"- {field['name']}: {field['description']}"
            for field in fields
        ])
        
        # Create JSON structure example
        json_structure = json.dumps({
            field['name']: f"<{field['name']}>"
            for field in fields
        }, indent=2)
        
        # Format examples if provided
        examples_text = ""
        if examples:
            examples_text = "Examples:\n"
            for example in examples:
                examples_text += f"Text: {example['text']}\n"
                examples_text += f"Output: {json.dumps(example['output'], indent=2)}\n\n"
        
        # Format domain-specific instructions
        domain_instructions = ""
        if domain == "medical":
            domain_instructions = """
            For medical terms, use standard medical terminology.
            For dates, use ISO format (YYYY-MM-DD).
            """
        elif domain == "legal":
            domain_instructions = """
            For legal references, maintain exact formatting.
            For dates, use ISO format (YYYY-MM-DD).
            """
        
        # Combine all parts
        prompt = template.format(
            field_descriptions=field_descriptions,
            json_structure=json_structure,
            text=chunk_text,
            examples=examples_text,
            domain_instructions=domain_instructions
        )
        
        return prompt
```

### ResponseParser
```python
import json
from typing import Dict, Any, Tuple, Optional
import re

class ResponseParser:
    """Parses and validates LLM responses."""
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If response cannot be parsed as JSON
        """
        # Try to find JSON in the response (in case model adds explanations)
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Look for anything that looks like a JSON object
            json_match = re.search(r'(\{[\s\S]*\})', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to clean up the response
            cleaned_json = self._clean_json_string(json_str)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse JSON response: {e}")
    
    def _clean_json_string(self, json_str: str) -> str:
        """
        Attempt to clean up malformed JSON.
        
        Args:
            json_str: Potentially malformed JSON string
            
        Returns:
            Cleaned JSON string
        """
        # Remove any leading/trailing non-JSON content
        json_str = re.sub(r'^[^{]*', '', json_str)
        json_str = re.sub(r'[^}]*$', '', json_str)
        
        # Fix common JSON errors
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
        
        return json_str
    
    def validate_fields(self, extracted_data: Dict[str, Any], 
                       expected_fields: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Validate extracted fields against expected fields.
        
        Args:
            extracted_data: Parsed data from LLM
            expected_fields: Field definitions with validation rules
            
        Returns:
            Tuple of (validated_data, validation_issues)
        """
        validated_data = {}
        validation_issues = {}
        
        for field in expected_fields:
            field_name = field['name']
            
            # Check if field exists
            if field_name not in extracted_data:
                validation_issues[field_name] = "Field missing in response"
                validated_data[field_name] = None
                continue
            
            value = extracted_data[field_name]
            
            # Skip validation for null values
            if value is None:
                validated_data[field_name] = None
                continue
            
            # Validate based on field type
            if field.get('type') == 'date' and value:
                # Validate date format
                if not self._is_valid_date(value):
                    validation_issues[field_name] = f"Invalid date format: {value}"
                    # Attempt to fix date
                    fixed_date = self._fix_date_format(value)
                    if fixed_date:
                        validated_data[field_name] = fixed_date
                    else:
                        validated_data[field_name] = value
                else:
                    validated_data[field_name] = value
            elif field.get('type') == 'number' and value:
                # Validate number
                try:
                    validated_data[field_name] = float(value)
                except (ValueError, TypeError):
                    validation_issues[field_name] = f"Invalid number: {value}"
                    validated_data[field_name] = value
            else:
                # String or other type
                validated_data[field_name] = value
            
            # Validate with regex if provided
            if field.get('validation_regex') and value and isinstance(value, str):
                if not re.match(field['validation_regex'], value):
                    validation_issues[field_name] = f"Failed regex validation: {value}"
        
        return validated_data, validation_issues
    
    def _is_valid_date(self, date_str: str) -> bool:
        """
        Check if string is a valid ISO date.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid ISO date
        """
        iso_pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(iso_pattern, date_str))
    
    def _fix_date_format(self, date_str: str) -> Optional[str]:
        """
        Attempt to fix common date format issues.
        
        Args:
            date_str: Malformed date string
            
        Returns:
            Fixed date string or None if unfixable
        """
        # Try common date formats
        patterns = [
            # MM/DD/YYYY
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: f"{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
            # DD/MM/YYYY
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', lambda m: f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"),
            # Month DD, YYYY
            (r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', self._convert_text_date)
        ]
        
        for pattern, formatter in patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    return formatter(match)
                except:
                    continue
        
        return None
    
    def _convert_text_date(self, match) -> str:
        """
        Convert text month to numeric.
        
        Args:
            match: Regex match object
            
        Returns:
            ISO formatted date
        """
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        
        month = match.group(1).lower()
        day = match.group(2).zfill(2)
        year = match.group(3)
        
        if month in month_map:
            return f"{year}-{month_map[month]}-{day}"
        
        return None
```

### FieldExtractor
```python
from typing import List, Dict, Any, Optional, Tuple

class FieldExtractor:
    """Extracts fields from document chunks."""
    
    def __init__(self, prompt_builder: PromptBuilder, 
                response_parser: ResponseParser,
                llm_processor: Any):  # Reference to ParallelProcessor
        """
        Initialize with builders and processors.
        
        Args:
            prompt_builder: For building extraction prompts
            response_parser: For parsing LLM responses
            llm_processor: For sending prompts to LLM
        """
        self.prompt_builder = prompt_builder
        self.response_parser = response_parser
        self.llm_processor = llm_processor
    
    async def extract_fields(self, chunk: DocumentChunk, 
                           field_definitions: List[Dict[str, Any]], 
                           domain: str,
                           examples: Optional[List[Dict[str, Any]]] = None) -> ExtractedFields:
        """
        Extract fields from a document chunk.
        
        Args:
            chunk: Document chunk to process
            field_definitions: Definitions of fields to extract
            domain: Domain context
            examples: Few-shot examples
            
        Returns:
            Extracted fields with metadata
        """
        # Build prompt
        prompt = self.prompt_builder.build_extraction_prompt(
            chunk_text=chunk.text,
            fields=field_definitions,
            domain=domain,
            examples=examples
        )
        
        # Process with LLM
        response = await self.llm_processor.llm_client.process_prompt(
            prompt=prompt,
            model_name="dudoxx-extract-1",  # Configurable
            temperature=0.0  # Deterministic for extraction
        )
        
        # Parse response
        try:
            extracted_data = self.response_parser.parse_json_response(response["content"])
        except ValueError as e:
            # Handle parsing error
            return ExtractedFields(
                chunk_index=chunk.index,
                fields={},
                confidence={},
                metadata={
                    "error": str(e),
                    "raw_response": response["content"],
                    "processing_metadata": response["metadata"]
                }
            )
        
        # Validate fields
        validated_data, validation_issues = self.response_parser.validate_fields(
            extracted_data=extracted_data,
            expected_fields=field_definitions
        )
        
        # Calculate confidence scores (simplified)
        confidence = self._calculate_confidence(validated_data, validation_issues)
        
        return ExtractedFields(
            chunk_index=chunk.index,
            fields=validated_data,
            confidence=confidence,
            metadata={
                "validation_issues": validation_issues,
                "processing_metadata": response["metadata"],
                "chunk_metadata": chunk.metadata
            }
        )
    
    def _calculate_confidence(self, data: Dict[str, Any], 
                            issues: Dict[str, str]) -> Dict[str, float]:
        """
        Calculate confidence scores for extracted fields.
        
        Args:
            data: Validated field data
            issues: Validation issues
            
        Returns:
            Confidence scores per field
        """
        confidence = {}
        
        for field_name, value in data.items():
            if field_name in issues:
                # Lower confidence for fields with issues
                confidence[field_name] = 0.5
            elif value is None:
                # Field not found
                confidence[field_name] = 0.0
            else:
                # Default confidence for valid fields
                confidence[field_name] = 1.0
        
        return confidence
```

## Features to Implement

1. **Dynamic Prompt Generation**
   - Support for domain-specific prompt templates
   - Field-driven prompt construction
   - Few-shot example integration
   - Context-aware prompting

2. **Robust Response Parsing**
   - JSON extraction from various response formats
   - Error recovery for malformed JSON
   - Structured data validation
   - Type conversion and normalization

3. **Field Validation**
   - Type-specific validation (dates, numbers, etc.)
   - Regex-based validation
   - Format correction for common issues
   - Confidence scoring

4. **Domain Adaptability**
   - Configuration-driven field definitions
   - Domain-specific extraction rules
   - Custom validation per domain
   - Extensible for new domains

5. **Performance Optimization**
   - Efficient prompt construction
   - Lightweight validation
   - Caching of common field definitions
   - Optimized JSON parsing

## Testing Strategy

### Unit Tests

1. **Prompt Builder Tests**
   - Test prompt generation for different domains
   - Verify field descriptions are correctly formatted
   - Test few-shot example integration
   - Verify prompt stays within token limits

2. **Response Parser Tests**
   - Test JSON extraction from various response formats
   - Verify handling of malformed JSON
   - Test field validation logic
   - Verify date format correction

3. **Field Extractor Tests**
   - Test end-to-end extraction with mock LLM
   - Verify confidence calculation
   - Test handling of missing fields
   - Verify metadata is correctly populated

### Integration Tests

1. **End-to-End Extraction Tests**
   - Test with real LLM responses
   - Verify correct handling of different field types
   - Test with various document types
   - Measure extraction accuracy

2. **Domain-Specific Tests**
   - Test extraction for medical documents
   - Test extraction for legal documents
   - Test extraction for financial documents
   - Verify domain-specific rules are applied

### Accuracy Tests

1. **Field Extraction Accuracy**
   - Compare extracted fields to ground truth
   - Measure precision and recall
   - Evaluate confidence score correlation with accuracy
   - Test with challenging document formats

2. **Edge Case Tests**
   - Test with fields spanning multiple chunks
   - Test with ambiguous field values
   - Test with conflicting information
   - Test with poorly formatted documents

## Example Usage

```python
import asyncio
from typing import List, Dict, Any

async def main():
    # Initialize components
    prompt_builder = PromptBuilder()
    response_parser = ResponseParser()
    
    # Initialize LLM client (simplified)
    llm_client = OpenAICompatibleClient(
        api_key="your-api-key",
        base_url="https://api.dudoxx.ai/v1"
    )
    
    # Initialize parallel processor
    processor = ParallelProcessor(
        llm_client=llm_client,
        max_concurrency=20
    )
    
    # Initialize field extractor
    extractor = FieldExtractor(
        prompt_builder=prompt_builder,
        response_parser=response_parser,
        llm_processor=processor
    )
    
    # Define field definitions
    field_definitions = [
        {
            "name": "patient_name",
            "description": "Full name of the patient",
            "type": "string"
        },
        {
            "name": "date_of_birth",
            "description": "Patient's date of birth in YYYY-MM-DD format",
            "type": "date",
            "validation_regex": r"^\d{4}-\d{2}-\d{2}$"
        },
        {
            "name": "diagnosis",
            "description": "Primary medical diagnosis",
            "type": "string"
        }
    ]
    
    # Process a chunk
    chunk = DocumentChunk(
        text="Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
        index=0,
        metadata={}
    )
    
    # Extract fields
    extracted_fields = await extractor.extract_fields(
        chunk=chunk,
        field_definitions=field_definitions,
        domain="medical"
    )
    
    # Print results
    print("Extracted Fields:")
    for field_name, value in extracted_fields.fields.items():
        confidence = extracted_fields.confidence.get(field_name, 0.0)
        print(f"- {field_name}: {value} (confidence: {confidence:.2f})")
    
    # Check for issues
    if extracted_fields.metadata.get("validation_issues"):
        print("\nValidation Issues:")
        for field, issue in extracted_fields.metadata["validation_issues"].items():
            print(f"- {field}: {issue}")

# Run the async function
asyncio.run(main())
