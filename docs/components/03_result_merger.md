# Result Merger

The `ResultMerger` is a critical component in the Dudoxx Extraction system that handles the merging and deduplication of results from multiple document chunks.

## Overview

When processing large documents, the extraction pipeline splits the document into manageable chunks and processes each chunk independently. This approach allows for parallel processing but requires a mechanism to merge the results from all chunks into a coherent final result. The `ResultMerger` serves this purpose by combining the extracted information from all chunks while eliminating duplicates.

## Key Features

1. **Result Merging**: Combines results from multiple document chunks
2. **Deduplication**: Eliminates duplicate information using semantic similarity
3. **Confidence Scoring**: Assigns confidence scores to merged results
4. **Metadata Tracking**: Maintains metadata about the source of each piece of information
5. **Vector-Based Deduplication**: Uses embeddings for semantic deduplication of text items

## Implementation

The `ResultMerger` class is implemented in the extraction pipeline. Here's a simplified version of the class:

```python
class ResultMerger:
    def __init__(self, embedding_model=None, deduplication_threshold=0.9, logger=None):
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.deduplication_threshold = deduplication_threshold
        self.logger = logger
    
    def merge_results(self, chunk_results):
        if self.logger:
            self.logger.log_step("Result Merging", f"Merging results from {len(chunk_results)} chunks")
            
        merged_fields = {}
        field_sources = {}
        field_confidences = {}
        
        # Collect all field values
        for i, result in enumerate(chunk_results):
            for field_name, value in result.items():
                if field_name not in merged_fields:
                    merged_fields[field_name] = []
                    field_sources[field_name] = []
                    field_confidences[field_name] = []
                
                merged_fields[field_name].append(value)
                field_sources[field_name].append(i)
                # Assuming confidence is 1.0 if not provided
                field_confidences[field_name].append(1.0)
        
        # Deduplicate and merge
        final_result = {}
        for field_name, values in merged_fields.items():
            if len(values) == 1:
                # Only one value, no need to deduplicate
                final_result[field_name] = values[0]
            else:
                # Multiple values, need to deduplicate
                if isinstance(values[0], list):
                    # Field is a list, merge all items and deduplicate
                    all_items = []
                    for value in values:
                        if value is not None:
                            all_items.extend(value)
                    final_result[field_name] = self._deduplicate_list(all_items)
                else:
                    # Field is a single value, choose the most confident one
                    best_index = np.argmax(field_confidences[field_name])
                    final_result[field_name] = values[best_index]
        
        # Add metadata
        final_result["_metadata"] = {
            "source_chunks": field_sources,
            "confidence": field_confidences
        }
        
        return final_result
    
    def _deduplicate_list(self, items):
        if not items:
            return []
        
        if all(isinstance(item, str) for item in items):
            # Text items, use embeddings for deduplication
            unique_items = []
            
            # Create vector store with first item
            vector_store = FAISS.from_texts([items[0]], self.embedding_model)
            unique_items.append(items[0])
            
            # Check each item against vector store
            for item in items[1:]:
                results = vector_store.similarity_search_with_score(item, k=1)
                
                if not results or results[0][1] > self.deduplication_threshold:
                    # Item is unique, add to vector store and unique items
                    vector_store.add_texts([item])
                    unique_items.append(item)
            
            return unique_items
        else:
            # Non-text items, use equality for deduplication
            unique_items = list(set(items))
            
            return unique_items
```

## Merging Process

1. **Collection**: Collect all field values from all chunks, along with their sources and confidence scores.
2. **Deduplication**: For each field, deduplicate the values based on the field type:
   - For list fields, merge all items and deduplicate the combined list.
   - For single-value fields, choose the value with the highest confidence score.
3. **Metadata**: Add metadata to the final result, including the source chunks and confidence scores for each field.

## Deduplication Process

The deduplication process depends on the type of items being deduplicated:

1. **Text Items**: For text items, the merger uses vector embeddings to perform semantic deduplication:
   - Create a vector store with the first item.
   - For each subsequent item, check its similarity to existing items in the vector store.
   - If the similarity is below the threshold, add the item to the vector store and the unique items list.
2. **Non-Text Items**: For non-text items, the merger uses equality-based deduplication:
   - Convert the list to a set to remove duplicates.
   - Convert the set back to a list.

## Usage Example

```python
# Initialize components
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
logger = RichLogger(verbose=True)

# Create result merger
merger = ResultMerger(embedding_model=embedding_model, deduplication_threshold=0.9, logger=logger)

# Merge results from multiple chunks
chunk_results = [
    {
        "patient_name": "John Smith",
        "diagnoses": ["Type 2 Diabetes", "Hypertension"]
    },
    {
        "patient_name": "John Smith",
        "diagnoses": ["Hypertension", "Upper respiratory infection"]
    }
]
merged_result = merger.merge_results(chunk_results)
print(merged_result)
```

## Integration with Extraction Pipeline

The `ResultMerger` is integrated into the extraction pipeline and is used to merge the results from all chunks:

```python
# In ExtractionPipeline.process_document
# Step 5: Merge and deduplicate results
merged_result = self.result_merger.merge_results(normalized_results)
```

## Benefits

1. **Coherent Results**: Produces a single, coherent result from multiple document chunks.
2. **Reduced Redundancy**: Eliminates duplicate information to provide a cleaner result.
3. **Semantic Deduplication**: Uses vector embeddings for semantic deduplication, which can identify similar but not identical items.
4. **Confidence Scoring**: Assigns confidence scores to help choose the best value when there are conflicts.
5. **Metadata Tracking**: Maintains metadata about the source of each piece of information, which can be useful for debugging and analysis.

## Customization

The `ResultMerger` can be customized in several ways:

1. **Embedding Model**: Use a different embedding model for semantic deduplication.
2. **Deduplication Threshold**: Adjust the threshold for semantic similarity to control the strictness of deduplication.
3. **Confidence Scoring**: Implement custom confidence scoring logic.
4. **Merging Logic**: Customize the merging logic for specific field types.
