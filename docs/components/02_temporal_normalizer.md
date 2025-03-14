# Temporal Normalizer

The `TemporalNormalizer` is a specialized component in the Dudoxx Extraction system that handles the normalization of dates and the construction of timelines from extracted data.

## Overview

When extracting information from documents, dates can appear in various formats (e.g., "05/15/1980", "May 15, 1980", "15-05-1980"). The `TemporalNormalizer` converts these diverse date formats into a standardized format (YYYY-MM-DD) for consistency and easier processing.

Additionally, it can construct timelines by sorting events based on their normalized dates, which is particularly useful for medical records, legal documents, and other time-sensitive information.

## Key Features

1. **Date Normalization**: Converts dates in various formats to a standardized YYYY-MM-DD format
2. **Format Detection**: Automatically detects common date formats
3. **LLM-Assisted Parsing**: Uses LLM for complex date formats that can't be parsed with standard methods
4. **Timeline Construction**: Sorts events chronologically based on normalized dates

## Implementation

The `TemporalNormalizer` class is implemented in the extraction pipeline. Here's a simplified version of the class:

```python
class TemporalNormalizer:
    def __init__(self, llm, logger=None):
        self.llm = llm
        self.logger = logger
        self.date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y"
        ]
    
    def normalize_date(self, date_string):
        if not date_string or not isinstance(date_string, str):
            return None
            
        # Try pattern matching first
        for date_format in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If pattern matching fails, use LLM for complex cases
        if self.logger:
            self.logger.log_step("Date Normalization", f"Using LLM to normalize date: {date_string}")
            
        prompt = PromptTemplate(
            template="Convert the following date to YYYY-MM-DD format: {date}",
            input_variables=["date"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(date=date_string)
        
        # Extract date using regex
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', result)
        if date_match:
            normalized_date = date_match.group(0)
            return normalized_date
        
        return None
    
    def construct_timeline(self, events):
        if not events:
            return []
            
        # Normalize dates
        for event in events:
            if "date" in event:
                normalized_date = self.normalize_date(event["date"])
                if normalized_date:
                    event["normalized_date"] = normalized_date
        
        # Sort events by normalized date
        sorted_events = sorted(
            events, 
            key=lambda x: x.get("normalized_date", x.get("date", ""))
        )
        
        return sorted_events
```

## Date Normalization Process

1. **Standard Format Parsing**: The normalizer first attempts to parse the date using standard Python datetime parsing with a list of common date formats.
2. **LLM-Assisted Parsing**: If standard parsing fails, it uses the LLM to interpret and convert the date.
3. **Regex Extraction**: After LLM processing, it extracts the normalized date using a regex pattern.
4. **Fallback**: If all methods fail, it returns None to indicate that the date couldn't be normalized.

## Timeline Construction Process

1. **Date Normalization**: For each event in the list, normalize the date field.
2. **Sorting**: Sort the events based on the normalized date.
3. **Return**: Return the sorted list of events.

## Usage Example

```python
# Initialize components
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
logger = RichLogger(verbose=True)

# Create temporal normalizer
normalizer = TemporalNormalizer(llm, logger)

# Normalize a date
normalized_date = normalizer.normalize_date("May 15, 1980")
print(normalized_date)  # Output: "1980-05-15"

# Construct a timeline
events = [
    {"date": "07/22/2023", "description": "Routine check-up"},
    {"date": "03/10/2023", "description": "Initial consultation"},
    {"date": "11/15/2023", "description": "Follow-up appointment"}
]
timeline = normalizer.construct_timeline(events)
for event in timeline:
    print(f"{event.get('normalized_date', event['date'])}: {event['description']}")
```

## Integration with Extraction Pipeline

The `TemporalNormalizer` is integrated into the extraction pipeline and is used to normalize dates in the extracted data:

```python
# In ExtractionPipeline.process_document
# Step 4: Normalize temporal data
normalized_results = []
for result in chunk_results:
    normalized_result = {}
    
    for field, value in result.items():
        if field.endswith("_date") or field == "date":
            # Normalize date fields
            normalized_result[field] = self.temporal_normalizer.normalize_date(value)
        elif field == "timeline" and isinstance(value, list):
            # Normalize timeline
            normalized_result[field] = self.temporal_normalizer.construct_timeline(value)
        else:
            normalized_result[field] = value
    
    normalized_results.append(normalized_result)
```

## Benefits

1. **Consistency**: Ensures all dates are in a consistent format for easier processing and comparison.
2. **Robustness**: Handles a wide variety of date formats, including complex and ambiguous ones.
3. **Chronological Ordering**: Enables chronological ordering of events for timeline construction.
4. **Improved Data Quality**: Enhances the quality of extracted data by standardizing temporal information.

## Customization

The `TemporalNormalizer` can be customized in several ways:

1. **Date Formats**: Add or remove date formats from the `date_formats` list.
2. **Output Format**: Change the output format from YYYY-MM-DD to any other format.
3. **LLM Prompt**: Customize the prompt used for LLM-assisted parsing.
4. **Sorting Logic**: Modify the sorting logic for timeline construction.
