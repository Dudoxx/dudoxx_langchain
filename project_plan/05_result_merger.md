# Result Merger & Deduplicator

## Business Description

The Result Merger & Deduplicator is responsible for combining the results from multiple processed chunks into a unified structured output. After all chunks have been processed by the LLM in parallel, this component collates field values from each chunk into a single record for the entire document. It intelligently handles cases where the same field appears in multiple chunks, either by deduplicating repeated information or by preserving distinct instances based on context.

The Result Merger & Deduplicator is designed to:
- Merge field values from multiple chunks into a coherent whole
- Deduplicate redundant data that appears across multiple chunks
- Disambiguate between repeated fields that represent distinct entities
- Detect and flag potential conflicts or inconsistencies
- Preserve the context and source of extracted information

## Dependencies

- **Field Extractor**: Provides the extracted fields from each chunk
- **Temporal Normalizer**: Provides normalized temporal data
- **Configuration Service**: For field-specific merging strategies
- **Logging Service**: For tracking merging operations
- **Error Handling Service**: For managing exceptions during merging

## Contracts

### Input
```python
class MergeRequest:
    extracted_chunks: List[ExtractedFields]  # Results from all chunks
    field_definitions: List[Dict[str, Any]]  # Definitions of fields
    domain: str  # Domain context (e.g., "medical", "legal")
```

### Output
```python
class MergedResult:
    fields: Dict[str, Any]  # Merged field values
    timeline: Optional[List[Dict[str, Any]]] = None  # Timeline if applicable
    metadata: Dict[str, Any]  # Merging metadata including:
        # - source_chunks: Dict[str, List[int]]  # Mapping of fields to source chunks
        # - conflicts: Dict[str, List[Any]]  # Fields with conflicting values
        # - confidence: Dict[str, float]  # Confidence scores for merged fields
```

## Core Classes

### FieldMergingStrategy (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class FieldMergingStrategy(ABC):
    """Abstract base class for field merging strategies."""
    
    @abstractmethod
    def merge_field_values(self, field_name: str, 
                          values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge values for a specific field from multiple chunks.
        
        Args:
            field_name: Name of the field to merge
            values: List of dictionaries containing:
                - value: The field value
                - chunk_index: Source chunk index
                - confidence: Confidence score
                - metadata: Additional metadata
                
        Returns:
            Dictionary containing:
                - value: Merged value
                - source_chunks: List of source chunk indices
                - confidence: Overall confidence score
                - conflicts: List of conflicting values if any
        """
        pass
```

### Concrete Merging Strategy Implementations

#### UniqueFieldMergingStrategy
```python
class UniqueFieldMergingStrategy(FieldMergingStrategy):
    """Strategy for fields that should have a single unique value."""
    
    def merge_field_values(self, field_name: str, 
                          values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge values for a field that should have a single unique value.
        
        Args:
            field_name: Name of the field to merge
            values: List of value dictionaries
            
        Returns:
            Merged result with highest confidence value
        """
        if not values:
            return {
                "value": None,
                "source_chunks": [],
                "confidence": 0.0,
                "conflicts": []
            }
            
        # Sort by confidence (descending)
        sorted_values = sorted(
            values, 
            key=lambda x: x.get("confidence", 0.0),
            reverse=True
        )
        
        # Get highest confidence value
        best_value = sorted_values[0]
        
        # Check for conflicts (different values)
        conflicts = []
        for value in sorted_values[1:]:
            if value["value"] != best_value["value"]:
                conflicts.append(value)
        
        return {
            "value": best_value["value"],
            "source_chunks": [v["chunk_index"] for v in values],
            "confidence": best_value.get("confidence", 0.0),
            "conflicts": conflicts if conflicts else []
        }
```

#### ListFieldMergingStrategy
```python
class ListFieldMergingStrategy(FieldMergingStrategy):
    """Strategy for fields that can have multiple values."""
    
    def __init__(self, deduplication_threshold: float = 0.9):
        """
        Initialize with deduplication threshold.
        
        Args:
            deduplication_threshold: Similarity threshold for deduplication
        """
        self.deduplication_threshold = deduplication_threshold
    
    def merge_field_values(self, field_name: str, 
                          values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge values for a field that can have multiple values.
        
        Args:
            field_name: Name of the field to merge
            values: List of value dictionaries
            
        Returns:
            Merged result with deduplicated list of values
        """
        if not values:
            return {
                "value": [],
                "source_chunks": [],
                "confidence": 0.0,
                "conflicts": []
            }
            
        # Extract all values
        all_values = []
        source_chunks = []
        
        for value_dict in values:
            value = value_dict["value"]
            chunk_index = value_dict["chunk_index"]
            
            # Handle both single values and lists
            if isinstance(value, list):
                for item in value:
                    all_values.append({
                        "value": item,
                        "chunk_index": chunk_index,
                        "confidence": value_dict.get("confidence", 0.0)
                    })
            elif value is not None:
                all_values.append({
                    "value": value,
                    "chunk_index": chunk_index,
                    "confidence": value_dict.get("confidence", 0.0)
                })
                
            source_chunks.append(chunk_index)
        
        # Deduplicate values
        deduplicated_values = self._deduplicate_values(all_values)
        
        # Calculate average confidence
        confidence_values = [v.get("confidence", 0.0) for v in values if v.get("confidence") is not None]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        
        return {
            "value": [v["value"] for v in deduplicated_values],
            "source_chunks": source_chunks,
            "confidence": avg_confidence,
            "conflicts": []  # No conflicts for list fields
        }
    
    def _deduplicate_values(self, values: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate values based on similarity.
        
        Args:
            values: List of value dictionaries
            
        Returns:
            Deduplicated list of value dictionaries
        """
        if not values:
            return []
            
        # Sort by confidence (descending)
        sorted_values = sorted(
            values, 
            key=lambda x: x.get("confidence", 0.0),
            reverse=True
        )
        
        # Simple string-based deduplication
        # In a real implementation, this would use embeddings for semantic similarity
        deduplicated = []
        for value in sorted_values:
            # Skip None values
            if value["value"] is None:
                continue
                
            # Check if this value is a duplicate
            is_duplicate = False
            for existing in deduplicated:
                if self._are_similar(value["value"], existing["value"]):
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                deduplicated.append(value)
        
        return deduplicated
    
    def _are_similar(self, value1: Any, value2: Any) -> bool:
        """
        Check if two values are similar.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            True if values are similar
        """
        # Simple string comparison
        # In a real implementation, this would use embeddings for semantic similarity
        if isinstance(value1, str) and isinstance(value2, str):
            # Normalize strings for comparison
            v1 = value1.lower().strip()
            v2 = value2.lower().strip()
            
            # Exact match
            if v1 == v2:
                return True
                
            # Substring match
            if v1 in v2 or v2 in v1:
                return True
                
            # TODO: Implement more sophisticated similarity check
            # e.g., using embeddings or edit distance
        
        return value1 == value2
```

#### TimelineFieldMergingStrategy
```python
class TimelineFieldMergingStrategy(FieldMergingStrategy):
    """Strategy for timeline fields that need chronological merging."""
    
    def __init__(self, date_field: str, temporal_normalizer: Any = None):
        """
        Initialize with date field and normalizer.
        
        Args:
            date_field: Field containing the date
            temporal_normalizer: For normalizing dates
        """
        self.date_field = date_field
        self.temporal_normalizer = temporal_normalizer
    
    def merge_field_values(self, field_name: str, 
                          values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge timeline entries from multiple chunks.
        
        Args:
            field_name: Name of the field to merge
            values: List of value dictionaries
            
        Returns:
            Merged result with chronologically sorted timeline
        """
        if not values:
            return {
                "value": [],
                "source_chunks": [],
                "confidence": 0.0,
                "conflicts": []
            }
            
        # Extract all timeline entries
        all_entries = []
        source_chunks = []
        
        for value_dict in values:
            entries = value_dict["value"]
            chunk_index = value_dict["chunk_index"]
            
            if not entries:
                continue
                
            # Handle both single entries and lists
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and self.date_field in entry:
                        all_entries.append({
                            "entry": entry,
                            "chunk_index": chunk_index,
                            "confidence": value_dict.get("confidence", 0.0)
                        })
            elif isinstance(entries, dict) and self.date_field in entries:
                all_entries.append({
                    "entry": entries,
                    "chunk_index": chunk_index,
                    "confidence": value_dict.get("confidence", 0.0)
                })
                
            source_chunks.append(chunk_index)
        
        # Deduplicate and sort entries
        merged_timeline = self._merge_timeline_entries(all_entries)
        
        # Calculate average confidence
        confidence_values = [v.get("confidence", 0.0) for v in values if v.get("confidence") is not None]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        
        return {
            "value": merged_timeline,
            "source_chunks": source_chunks,
            "confidence": avg_confidence,
            "conflicts": []  # No conflicts for timeline fields
        }
    
    def _merge_timeline_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge and sort timeline entries.
        
        Args:
            entries: List of entry dictionaries
            
        Returns:
            Merged and sorted timeline entries
        """
        if not entries:
            return []
            
        # Extract actual entries
        timeline_entries = [e["entry"] for e in entries]
        
        # Normalize dates if temporal normalizer is available
        if self.temporal_normalizer:
            for entry in timeline_entries:
                if self.date_field in entry:
                    date_str = entry[self.date_field]
                    normalized_date, _ = self.temporal_normalizer.date_normalizer.normalize_date(date_str)
                    if normalized_date:
                        entry[self.date_field] = normalized_date
        
        # Deduplicate entries
        deduplicated = self._deduplicate_timeline_entries(timeline_entries)
        
        # Sort by date
        sorted_entries = sorted(
            deduplicated,
            key=lambda x: x.get(self.date_field, "")
        )
        
        return sorted_entries
    
    def _deduplicate_timeline_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate timeline entries.
        
        Args:
            entries: List of timeline entries
            
        Returns:
            Deduplicated entries
        """
        if not entries:
            return []
            
        # Group by date
        date_groups = {}
        for entry in entries:
            date = entry.get(self.date_field)
            if not date:
                continue
                
            if date not in date_groups:
                date_groups[date] = []
                
            date_groups[date].append(entry)
        
        # Merge entries with same date
        deduplicated = []
        for date, date_entries in date_groups.items():
            if len(date_entries) == 1:
                deduplicated.append(date_entries[0])
            else:
                # Merge entries with same date
                merged_entry = {self.date_field: date}
                
                # Merge other fields
                for entry in date_entries:
                    for field, value in entry.items():
                        if field == self.date_field:
                            continue
                            
                        if field not in merged_entry:
                            merged_entry[field] = value
                        elif isinstance(merged_entry[field], list):
                            if isinstance(value, list):
                                merged_entry[field].extend(value)
                            else:
                                merged_entry[field].append(value)
                        else:
                            merged_entry[field] = [merged_entry[field], value]
                
                deduplicated.append(merged_entry)
        
        return deduplicated
```

### Deduplicator
```python
from typing import List, Dict, Any, Optional, Tuple

class Deduplicator:
    """Deduplicates field values across chunks."""
    
    def __init__(self, embedding_model: Optional[Any] = None,
                similarity_threshold: float = 0.9):
        """
        Initialize with optional embedding model.
        
        Args:
            embedding_model: Model for semantic similarity
            similarity_threshold: Threshold for deduplication
        """
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
    
    def deduplicate_fields(self, field_values: List[Tuple[str, Any, int]]) -> List[Tuple[str, Any, int]]:
        """
        Deduplicate field values.
        
        Args:
            field_values: List of (field_name, value, chunk_index) tuples
            
        Returns:
            Deduplicated list of (field_name, value, chunk_index) tuples
        """
        if not field_values:
            return []
            
        # Group by field name
        field_groups = {}
        for field_name, value, chunk_index in field_values:
            if field_name not in field_groups:
                field_groups[field_name] = []
                
            field_groups[field_name].append((value, chunk_index))
        
        # Deduplicate each field group
        deduplicated = []
        for field_name, values in field_groups.items():
            unique_values = self._deduplicate_value_group(values)
            
            for value, chunk_index in unique_values:
                deduplicated.append((field_name, value, chunk_index))
        
        return deduplicated
    
    def _deduplicate_value_group(self, values: List[Tuple[Any, int]]) -> List[Tuple[Any, int]]:
        """
        Deduplicate a group of values for the same field.
        
        Args:
            values: List of (value, chunk_index) tuples
            
        Returns:
            Deduplicated list of (value, chunk_index) tuples
        """
        if not values:
            return []
            
        # Handle None values
        values = [(v, c) for v, c in values if v is not None]
        
        if not values:
            return []
            
        if len(values) == 1:
            return values
            
        # For string values, use semantic similarity if embedding model is available
        if isinstance(values[0][0], str) and self.embedding_model:
            return self._deduplicate_with_embeddings(values)
        else:
            # Simple equality-based deduplication
            unique_values = []
            for value, chunk_index in values:
                if not any(self._are_equal(value, v) for v, _ in unique_values):
                    unique_values.append((value, chunk_index))
            
            return unique_values
    
    def _deduplicate_with_embeddings(self, values: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """
        Deduplicate string values using embeddings.
        
        Args:
            values: List of (value, chunk_index) tuples
            
        Returns:
            Deduplicated list of (value, chunk_index) tuples
        """
        # This is a placeholder for embedding-based deduplication
        # In a real implementation, this would use the embedding model
        
        # For now, just use string similarity
        unique_values = []
        for value, chunk_index in values:
            if not any(self._are_similar(value, v) for v, _ in unique_values):
                unique_values.append((value, chunk_index))
        
        return unique_values
    
    def _are_equal(self, value1: Any, value2: Any) -> bool:
        """
        Check if two values are equal.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            True if values are equal
        """
        if isinstance(value1, str) and isinstance(value2, str):
            return value1.lower().strip() == value2.lower().strip()
        else:
            return value1 == value2
    
    def _are_similar(self, value1: str, value2: str) -> bool:
        """
        Check if two strings are similar.
        
        Args:
            value1: First string
            value2: Second string
            
        Returns:
            True if strings are similar
        """
        # Normalize strings
        v1 = value1.lower().strip()
        v2 = value2.lower().strip()
        
        # Exact match
        if v1 == v2:
            return True
            
        # Substring match
        if v1 in v2 or v2 in v1:
            return True
            
        # TODO: Implement more sophisticated similarity check
        # e.g., using embeddings or edit distance
        
        return False
```

### ConflictResolver
```python
from typing import List, Dict, Any, Optional, Tuple

class ConflictResolver:
    """Resolves conflicts between field values."""
    
    def resolve_conflicts(self, field_name: str, 
                         conflicting_values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflicts for a field.
        
        Args:
            field_name: Name of the field
            conflicting_values: List of conflicting values with metadata
            
        Returns:
            Resolved value with metadata
        """
        if not conflicting_values:
            return {
                "value": None,
                "confidence": 0.0,
                "resolution_method": "none"
            }
            
        # Sort by confidence (descending)
        sorted_values = sorted(
            conflicting_values, 
            key=lambda x: x.get("confidence", 0.0),
            reverse=True
        )
        
        # Default to highest confidence value
        best_value = sorted_values[0]
        
        return {
            "value": best_value["value"],
            "confidence": best_value.get("confidence", 0.0),
            "resolution_method": "highest_confidence",
            "alternatives": [v["value"] for v in sorted_values[1:]]
        }
```

### ResultMerger
```python
from typing import List, Dict, Any, Optional

class ResultMerger:
    """Merges results from multiple chunks."""
    
    def __init__(self, field_strategies: Dict[str, FieldMergingStrategy],
                default_strategy: FieldMergingStrategy,
                deduplicator: Deduplicator,
                conflict_resolver: ConflictResolver):
        """
        Initialize with strategies and resolvers.
        
        Args:
            field_strategies: Field-specific merging strategies
            default_strategy: Default strategy for fields without specific strategy
            deduplicator: For deduplicating values
            conflict_resolver: For resolving conflicts
        """
        self.field_strategies = field_strategies
        self.default_strategy = default_strategy
        self.deduplicator = deduplicator
        self.conflict_resolver = conflict_resolver
    
    def merge_results(self, extracted_chunks: List[ExtractedFields],
                     field_definitions: List[Dict[str, Any]]) -> MergedResult:
        """
        Merge results from multiple chunks.
        
        Args:
            extracted_chunks: Results from all chunks
            field_definitions: Definitions of fields
            
        Returns:
            Merged result
        """
        # Group field values by field name
        field_values = {}
        for chunk in extracted_chunks:
            for field_name, value in chunk.fields.items():
                if field_name not in field_values:
                    field_values[field_name] = []
                    
                field_values[field_name].append({
                    "value": value,
                    "chunk_index": chunk.chunk_index,
                    "confidence": chunk.confidence.get(field_name, 0.0),
                    "metadata": chunk.metadata
                })
        
        # Merge each field
        merged_fields = {}
        source_chunks = {}
        conflicts = {}
        confidence = {}
        
        for field_name, values in field_values.items():
            # Get field definition
            field_def = next((f for f in field_definitions if f["name"] == field_name), None)
            
            # Get merging strategy
            strategy = self.field_strategies.get(field_name)
            if not strategy and field_def:
                # Use strategy based on field type
                field_type = field_def.get("type", "string")
                is_unique = field_def.get("is_unique", True)
                
                if field_type == "timeline":
                    date_field = field_def.get("date_field", "date")
                    strategy = TimelineFieldMergingStrategy(date_field=date_field)
                elif not is_unique:
                    strategy = ListFieldMergingStrategy()
                else:
                    strategy = UniqueFieldMergingStrategy()
            
            if not strategy:
                strategy = self.default_strategy
            
            # Merge field values
            merged_result = strategy.merge_field_values(field_name, values)
            
            merged_fields[field_name] = merged_result["value"]
            source_chunks[field_name] = merged_result["source_chunks"]
            confidence[field_name] = merged_result["confidence"]
            
            if merged_result["conflicts"]:
                conflicts[field_name] = merged_result["conflicts"]
                
                # Resolve conflicts
                resolution = self.conflict_resolver.resolve_conflicts(
                    field_name, merged_result["conflicts"]
                )
                
                # Update with resolved value if different
                if resolution["value"] != merged_fields[field_name]:
                    merged_fields[field_name] = resolution["value"]
                    confidence[field_name] = resolution["confidence"]
        
        # Extract timeline if present
        timeline = None
        timeline_field = next((f["name"] for f in field_definitions if f.get("type") == "timeline"), None)
        if timeline_field and timeline_field in merged_fields:
            timeline = merged_fields[timeline_field]
        
        return MergedResult(
            fields=merged_fields,
            timeline=timeline,
            metadata={
                "source_chunks": source_chunks,
                "conflicts": conflicts,
                "confidence": confidence
            }
        )
```

## Features to Implement

1. **Intelligent Field Merging**
   - Strategy pattern for different field types
   - Context-aware merging decisions
   - Support for both unique and list-based fields
   - Timeline construction from temporal data

2. **Semantic Deduplication**
   - Embedding-based similarity detection
   - Configurable similarity thresholds
   - Handling of slight variations in text
   - Preservation of unique instances

3. **Conflict Resolution**
   - Detection of contradictory field values
   - Confidence-based resolution strategies
   - Preservation of alternative values
   - Flagging of unresolvable conflicts

4. **Context Preservation**
   - Tracking of source chunks for each field
   - Metadata about merging decisions
   - Confidence scoring for merged results
   - Audit trail for extracted information

5. **Domain-Specific Merging**
   - Customizable merging strategies per domain
   - Field-specific merging rules
   - Support for complex nested structures
   - Handling of domain-specific data types

## Testing Strategy

### Unit Tests

1. **Strategy Tests**
   - Test each merging strategy independently
   - Verify correct handling of different field types
   - Test conflict detection and resolution
   - Verify source tracking

2. **Deduplication Tests**
   - Test string-based deduplication
   - Verify embedding-based similarity detection
   - Test handling of slight variations
   - Verify preservation of unique instances

3. **Edge Case Tests**
   - Test with empty or null values
   - Verify handling of conflicting information
   - Test with single vs. multiple chunks
   - Verify handling of missing fields

### Integration Tests

1. **End-to-End Merging Tests**
   - Test with real extracted data from multiple chunks
   - Verify correct merging of different field types
   - Test with various document types
   - Measure merging accuracy

2. **Domain-Specific Tests**
   - Test with medical records
   - Test with legal documents
   - Test with financial reports
   - Verify domain-specific merging rules

### Accuracy Tests

1. **Deduplication Accuracy**
   - Measure precision and recall of deduplication
   - Compare with ground truth for merged fields
   - Evaluate handling of near-duplicates
   - Test with challenging edge cases

2. **Conflict Resolution Accuracy**
   - Evaluate accuracy of conflict resolution
   - Measure correlation between confidence and correctness
   - Test with deliberately conflicting data
   - Verify preservation of important alternatives

## Example Usage

```python
from typing import List, Dict, Any

def main():
    # Initialize strategies
    unique_strategy = UniqueFieldMergingStrategy()
    list_strategy = ListFieldMergingStrategy(deduplication_threshold=0.9)
    timeline_strategy = TimelineFieldMergingStrategy(date_field="date")
    
    # Initialize components
    deduplicator = Deduplicator(similarity_threshold=0.9)
    conflict_resolver = ConflictResolver()
    
    # Field-specific strategies
    field_strategies = {
        "patient_name": unique_strategy,
        "date_of_birth": unique_strategy,
        "diagnoses": list_strategy,
        "medications": list_strategy,
        "visits": timeline_strategy
    }
    
    # Initialize merger
    merger = ResultMerger(
        field_strategies=field_strategies,
        default_strategy=unique_strategy,
        deduplicator=deduplicator,
        conflict_resolver=conflict_resolver
    )
    
    # Sample extracted chunks
    chunk1 = ExtractedFields(
        chunk_index=0,
        fields={
            "patient_name": "John Doe",
            "date_of_birth": "1980-05-15",
            "diagnoses": ["Diabetes mellitus Type II"]
        },
        confidence={
            "patient_name": 0.9,
            "date_of_birth": 0.8,
            "diagnoses": 0.7
        },
        metadata={}
    )
    
    chunk2 = ExtractedFields(
        chunk_index=1,
        fields={
            "patient_name": "John A. Doe",
            "medications": ["Metformin", "Lisinopril"],
            "visits": [
                {"date": "2021-07-10", "description": "Patient reported dizziness"}
            ]
        },
        confidence={
            "patient_name": 0.7,
            "medications": 0.8,
            "visits": 0.9
        },
        metadata={}
    )
    
    chunk3 = ExtractedFields(
        chunk_index=2,
        fields={
            "diagnoses": ["Hypertension"],
            "medications": ["Lisinopril"],
            "visits": [
                {"date": "2021-08-20", "description": "Follow-up visit"}
            ]
        },
        confidence={
            "diagnoses": 0.8,
            "medications": 0.9,
            "visits": 0.9
        },
        metadata={}
    )
    
    # Field definitions
    field_definitions = [
        {"name": "patient_name", "type": "string", "is_unique": True},
        {"name": "date_of_birth", "type": "date", "is_unique": True},
        {"name": "diagnoses", "type": "string", "is_unique": False},
        {"name": "medications", "type": "string", "is_unique": False},
        {"name": "visits", "type": "timeline", "date_field": "date", "is_unique": False}
    ]
    
    # Merge results
    merged_result = merger.merge_results(
        extracted_chunks=[chunk1, chunk2, chunk3],
        field_definitions=field_definitions
    )
    
    # Print merged fields
    print("Merged Fields:")
    for field_name, value in merged_result.fields.items():
        confidence = merged_result.metadata["confidence"].get(field_name, 0.0)
        source_chunks = merged_result.metadata["source_chunks"].get(field_name, [])
        print(f"- {field_name}: {value} (confidence: {confidence:.2f}, sources: {source_chunks})")
    
    # Print conflicts if any
    if merged_result.metadata["conflicts"]:
        print("\nConflicts:")
        for field_name, conflicts in merged_result.metadata["conflicts"].items():
            print(f"- {field_name}: {[c['value'] for c in conflicts]}")
    
    # Print timeline if any
    if merged_result.timeline:
        print("\nTimeline:")
        for event in merged_result.timeline:
            print(f"- {event['date']}: {event['description']}")

# Run the function
main()
