# Temporal Normalizer

## Business Description

The Temporal Normalizer is responsible for standardizing all date/time values extracted from documents and constructing chronological timelines when appropriate. Many documents (especially in medical or legal domains) contain multiple dates and time-specific events. This component ensures that all temporal data is normalized into a consistent format (e.g., ISO 8601 YYYY-MM-DD for dates) and organizes time-based events into a coherent chronological sequence.

The Temporal Normalizer is designed to:
- Convert various date/time formats to a standardized representation
- Organize events chronologically when the content includes a series of events over time
- Preserve context for each event in the timeline
- Handle relative dates and time references
- Maintain the narrative flow of the original document's timeline

## Dependencies

- **Field Extractor**: Provides the extracted field values that may contain temporal data
- **Configuration Service**: For domain-specific date format settings
- **Logging Service**: For tracking normalization operations
- **Error Handling Service**: For managing exceptions during normalization

## Contracts

### Input
```python
class NormalizationRequest:
    extracted_data: Dict[str, Any]  # Data extracted from chunks
    temporal_fields: List[str]  # Fields containing date/time values
    timeline_config: Optional[Dict[str, Any]] = None  # Timeline configuration
    domain: str  # Domain context (e.g., "medical", "legal")
```

### Output
```python
class NormalizedData:
    data: Dict[str, Any]  # Normalized data with standardized dates
    timeline: Optional[List[Dict[str, Any]]] = None  # Chronological timeline if applicable
    metadata: Dict[str, Any]  # Normalization metadata
```

## Core Classes

### DateNormalizer
```python
from datetime import datetime
import re
from typing import Dict, Any, List, Optional, Tuple
import dateutil.parser

class DateNormalizer:
    """Normalizes dates to standard format."""
    
    def __init__(self, output_format: str = "%Y-%m-%d"):
        """
        Initialize with output format.
        
        Args:
            output_format: strftime format for output dates
        """
        self.output_format = output_format
        
        # Common date patterns for explicit parsing
        self.date_patterns = [
            # MM/DD/YYYY
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', 
             lambda m: f"{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
            # DD/MM/YYYY
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', 
             lambda m: f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"),
            # Month DD, YYYY
            (r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', self._convert_text_date)
        ]
    
    def normalize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Normalize date string to standard format.
        
        Args:
            date_str: Date string in any format
            
        Returns:
            Tuple of (normalized_date, success)
        """
        if not date_str or not isinstance(date_str, str):
            return None, False
            
        # Check if already in ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str, True
            
        # Try explicit patterns first
        for pattern, formatter in self.date_patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    return formatter(match), True
                except:
                    continue
        
        # Fall back to dateutil parser
        try:
            parsed_date = dateutil.parser.parse(date_str)
            return parsed_date.strftime(self.output_format), True
        except:
            return date_str, False
    
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
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'sept': '09',
            'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        month = match.group(1).lower()
        day = match.group(2).zfill(2)
        year = match.group(3)
        
        if month in month_map:
            return f"{year}-{month_map[month]}-{day}"
        
        return None
    
    def normalize_dates_in_data(self, data: Dict[str, Any], 
                               date_fields: List[str]) -> Tuple[Dict[str, Any], Dict[str, bool]]:
        """
        Normalize all date fields in data.
        
        Args:
            data: Data containing date fields
            date_fields: List of field names containing dates
            
        Returns:
            Tuple of (normalized_data, normalization_status)
        """
        normalized_data = data.copy()
        normalization_status = {}
        
        for field in date_fields:
            if field in data and data[field]:
                if isinstance(data[field], list):
                    # Handle list of dates
                    normalized_list = []
                    success_list = []
                    
                    for date_item in data[field]:
                        if isinstance(date_item, str):
                            normalized_date, success = self.normalize_date(date_item)
                            normalized_list.append(normalized_date)
                            success_list.append(success)
                        else:
                            normalized_list.append(date_item)
                            success_list.append(False)
                    
                    normalized_data[field] = normalized_list
                    normalization_status[field] = all(success_list)
                else:
                    # Handle single date
                    normalized_date, success = self.normalize_date(str(data[field]))
                    normalized_data[field] = normalized_date
                    normalization_status[field] = success
        
        return normalized_data, normalization_status
```

### TimelineBuilder
```python
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import copy

class TimelineBuilder:
    """Constructs chronological timelines from events."""
    
    def __init__(self, date_normalizer: DateNormalizer):
        """
        Initialize with date normalizer.
        
        Args:
            date_normalizer: For normalizing dates in events
        """
        self.date_normalizer = date_normalizer
    
    def construct_timeline(self, events: List[Dict[str, Any]], 
                          date_field: str, 
                          event_fields: List[str],
                          sort_ascending: bool = True) -> List[Dict[str, Any]]:
        """
        Construct timeline from events.
        
        Args:
            events: List of event dictionaries
            date_field: Field name containing event date
            event_fields: Fields to include in timeline events
            sort_ascending: Whether to sort from oldest to newest
            
        Returns:
            Chronologically sorted timeline
        """
        if not events:
            return []
            
        timeline = []
        
        for event in events:
            if date_field not in event or not event[date_field]:
                continue
                
            # Normalize date
            normalized_date, success = self.date_normalizer.normalize_date(
                str(event[date_field])
            )
            
            if not success:
                # Skip events with invalid dates
                continue
                
            # Create timeline entry
            timeline_entry = {
                "date": normalized_date,
                "data": {}
            }
            
            # Add event fields
            for field in event_fields:
                if field in event and field != date_field:
                    timeline_entry["data"][field] = event[field]
            
            timeline.append(timeline_entry)
        
        # Sort timeline
        timeline.sort(
            key=lambda x: x["date"],
            reverse=not sort_ascending
        )
        
        return timeline
    
    def merge_timeline_events(self, timeline: List[Dict[str, Any]], 
                             merge_window_days: int = 0) -> List[Dict[str, Any]]:
        """
        Merge events that occur on the same date or within window.
        
        Args:
            timeline: Timeline to merge
            merge_window_days: Days within which to merge events
            
        Returns:
            Timeline with merged events
        """
        if not timeline or merge_window_days < 0:
            return timeline
            
        if merge_window_days == 0:
            # Only merge same-day events
            date_groups = {}
            
            for event in timeline:
                date = event["date"]
                
                if date not in date_groups:
                    date_groups[date] = []
                    
                date_groups[date].append(event)
            
            merged_timeline = []
            
            for date, events in date_groups.items():
                if len(events) == 1:
                    merged_timeline.append(events[0])
                else:
                    # Merge events with same date
                    merged_event = {
                        "date": date,
                        "data": {}
                    }
                    
                    for event in events:
                        for field, value in event["data"].items():
                            if field not in merged_event["data"]:
                                merged_event["data"][field] = value
                            elif isinstance(merged_event["data"][field], list):
                                if isinstance(value, list):
                                    merged_event["data"][field].extend(value)
                                else:
                                    merged_event["data"][field].append(value)
                            else:
                                merged_event["data"][field] = [merged_event["data"][field], value]
                    
                    merged_timeline.append(merged_event)
            
            # Re-sort timeline
            merged_timeline.sort(key=lambda x: x["date"])
            
            return merged_timeline
        else:
            # Implement window-based merging for events within X days
            # This would require date parsing and comparison
            pass
```

### TemporalNormalizer
```python
from typing import Dict, Any, List, Optional, Tuple

class TemporalNormalizer:
    """Normalizes temporal data in extracted fields."""
    
    def __init__(self, date_normalizer: DateNormalizer, 
                timeline_builder: TimelineBuilder):
        """
        Initialize with normalizers and builders.
        
        Args:
            date_normalizer: For normalizing dates
            timeline_builder: For building timelines
        """
        self.date_normalizer = date_normalizer
        self.timeline_builder = timeline_builder
    
    def normalize(self, extracted_data: Dict[str, Any], 
                 temporal_fields: List[str],
                 timeline_config: Optional[Dict[str, Any]] = None) -> NormalizedData:
        """
        Normalize temporal data in extracted fields.
        
        Args:
            extracted_data: Data extracted from chunks
            temporal_fields: Fields containing date/time values
            timeline_config: Configuration for timeline construction
            
        Returns:
            Normalized data with standardized dates and timeline
        """
        # Normalize dates in all temporal fields
        normalized_data, normalization_status = self.date_normalizer.normalize_dates_in_data(
            data=extracted_data,
            date_fields=temporal_fields
        )
        
        # Build timeline if configured
        timeline = None
        if timeline_config:
            events_field = timeline_config.get("events_field")
            date_field = timeline_config.get("date_field")
            event_fields = timeline_config.get("event_fields", [])
            
            if events_field and date_field and events_field in normalized_data:
                events = normalized_data[events_field]
                
                if isinstance(events, list):
                    timeline = self.timeline_builder.construct_timeline(
                        events=events,
                        date_field=date_field,
                        event_fields=event_fields,
                        sort_ascending=timeline_config.get("sort_ascending", True)
                    )
                    
                    # Merge events if configured
                    if timeline_config.get("merge_same_day", False):
                        timeline = self.timeline_builder.merge_timeline_events(
                            timeline=timeline,
                            merge_window_days=timeline_config.get("merge_window_days", 0)
                        )
        
        return NormalizedData(
            data=normalized_data,
            timeline=timeline,
            metadata={
                "normalization_status": normalization_status,
                "timeline_config": timeline_config
            }
        )
    
    def extract_timeline_from_fields(self, data: Dict[str, Any],
                                   date_field: str,
                                   text_field: str) -> List[Dict[str, Any]]:
        """
        Extract timeline from fields with dates and descriptions.
        
        Args:
            data: Data containing date and text fields
            date_field: Field containing dates
            text_field: Field containing event descriptions
            
        Returns:
            Timeline constructed from fields
        """
        if date_field not in data or text_field not in data:
            return []
            
        dates = data[date_field]
        texts = data[text_field]
        
        # Ensure both are lists of the same length
        if not isinstance(dates, list):
            dates = [dates]
            
        if not isinstance(texts, list):
            texts = [texts]
            
        if len(dates) != len(texts):
            # Cannot match dates to texts
            return []
            
        # Construct events
        events = [
            {date_field: date, text_field: text}
            for date, text in zip(dates, texts)
        ]
        
        # Build timeline
        return self.timeline_builder.construct_timeline(
            events=events,
            date_field=date_field,
            event_fields=[text_field]
        )
```

## Features to Implement

1. **Date Format Normalization**
   - Support for various input date formats
   - Standardization to ISO 8601 (YYYY-MM-DD)
   - Handling of partial dates (year only, month/year)
   - Robust parsing with fallbacks

2. **Timeline Construction**
   - Chronological sorting of events
   - Handling of events with same date
   - Support for different timeline structures
   - Merging of related events

3. **Context Preservation**
   - Maintaining event details during normalization
   - Preserving relationships between events
   - Handling of events spanning multiple chunks
   - Contextual metadata for timeline entries

4. **Relative Date Handling**
   - Resolution of relative dates ("yesterday", "last week")
   - Handling of age references ("65-year-old")
   - Duration calculations ("for the past 3 months")
   - Reference date determination

5. **Domain-Specific Adaptations**
   - Medical-specific date handling
   - Legal document timeline construction
   - Financial report date normalization
   - Customizable per domain

## Testing Strategy

### Unit Tests

1. **Date Normalization Tests**
   - Test normalization of various date formats
   - Verify handling of invalid dates
   - Test normalization of date lists
   - Verify preservation of already-normalized dates

2. **Timeline Construction Tests**
   - Test chronological sorting
   - Verify handling of missing dates
   - Test event merging logic
   - Verify field inclusion in timeline

3. **Edge Case Tests**
   - Test with empty or null values
   - Verify handling of mixed formats
   - Test with extremely old or future dates
   - Verify handling of malformed dates

### Integration Tests

1. **End-to-End Normalization Tests**
   - Test with real extracted data
   - Verify correct handling of different field types
   - Test with various document types
   - Measure normalization accuracy

2. **Domain-Specific Tests**
   - Test with medical records
   - Test with legal documents
   - Test with financial reports
   - Verify domain-specific rules are applied

### Accuracy Tests

1. **Date Parsing Accuracy**
   - Compare normalized dates to ground truth
   - Measure success rate for different formats
   - Evaluate handling of ambiguous dates (MM/DD vs DD/MM)
   - Test with international date formats

2. **Timeline Accuracy Tests**
   - Verify events are in correct chronological order
   - Test with complex timelines from real documents
   - Verify context preservation in timeline
   - Test with events spanning multiple chunks

## Example Usage

```python
from datetime import datetime
from typing import Dict, Any, List

def main():
    # Initialize components
    date_normalizer = DateNormalizer(output_format="%Y-%m-%d")
    timeline_builder = TimelineBuilder(date_normalizer=date_normalizer)
    
    temporal_normalizer = TemporalNormalizer(
        date_normalizer=date_normalizer,
        timeline_builder=timeline_builder
    )
    
    # Sample extracted data
    extracted_data = {
        "patient_name": "John Doe",
        "date_of_birth": "05/15/1980",
        "admission_date": "January 10, 2023",
        "discharge_date": "2023-01-15",
        "visits": [
            {
                "visit_date": "12/20/2022",
                "symptoms": "Patient reported dizziness",
                "treatment": "Prescribed medication X"
            },
            {
                "visit_date": "01/05/2023",
                "symptoms": "Dizziness improved",
                "treatment": "Continued medication X"
            },
            {
                "visit_date": "2023-01-20",
                "symptoms": "Follow-up visit",
                "treatment": "Discontinued medication X"
            }
        ]
    }
    
    # Define temporal fields
    temporal_fields = ["date_of_birth", "admission_date", "discharge_date"]
    
    # Define timeline configuration
    timeline_config = {
        "events_field": "visits",
        "date_field": "visit_date",
        "event_fields": ["symptoms", "treatment"],
        "sort_ascending": True,
        "merge_same_day": True
    }
    
    # Normalize temporal data
    normalized_data = temporal_normalizer.normalize(
        extracted_data=extracted_data,
        temporal_fields=temporal_fields,
        timeline_config=timeline_config
    )
    
    # Print normalized data
    print("Normalized Data:")
    for field in temporal_fields:
        print(f"- {field}: {normalized_data.data[field]}")
    
    # Print timeline
    if normalized_data.timeline:
        print("\nTimeline:")
        for event in normalized_data.timeline:
            print(f"- {event['date']}:")
            for field, value in event['data'].items():
                print(f"  - {field}: {value}")

# Run the function
main()
