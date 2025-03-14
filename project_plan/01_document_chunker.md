# Document Chunker

## Business Description

The Document Chunker is responsible for intelligently segmenting large input texts into self-contained chunks that fit within the 16K token context window of the LLM. Instead of brute-force splitting at a fixed size, the system uses logical boundaries (e.g., section headings, paragraphs, or semantic breaks) to preserve context. This ensures each chunk contains a coherent portion of the text, maximizing relevant content per request.

The chunking strategy is designed to:
- Preserve context at chunk boundaries
- Ensure chunks are below the token limit (with buffer for prompts and output)
- Maximize the amount of relevant content per chunk
- Handle domain-specific document structures when available

## Dependencies

- **Configuration Service**: For domain-specific chunking strategies and settings
- **Logging Service**: For tracking chunking operations and potential issues
- **Error Handling Service**: For managing exceptions during chunking

## Contracts

### Input
```python
class ChunkingRequest:
    document: str  # The full text to process
    domain: str  # Domain context (e.g., "medical", "legal")
    max_chunk_size: int = 16000  # Maximum tokens per chunk (default: 16K)
    overlap_size: int = 200  # Number of tokens to overlap between chunks
    chunking_strategy: Optional[str] = None  # Override default strategy for domain
```

### Output
```python
class DocumentChunk:
    text: str  # The chunk text
    index: int  # Chunk index in sequence
    metadata: Dict[str, Any]  # Contains:
        # - start_position: int  # Character position in original document
        # - end_position: int  # End character position
        # - overlap_previous: bool  # Whether this chunk overlaps with previous
        # - overlap_next: bool  # Whether this chunk overlaps with next
        # - boundary_type: str  # Type of boundary used (e.g., "section", "paragraph")
```

## Core Classes

### ChunkingStrategy (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ChunkingStrategy(ABC):
    """Abstract base class for document chunking strategies."""
    
    @abstractmethod
    def chunk_document(self, document: str, max_chunk_size: int, 
                      overlap_size: int) -> List[DocumentChunk]:
        """
        Split a document into chunks according to the strategy.
        
        Args:
            document: The full text to process
            max_chunk_size: Maximum tokens per chunk
            overlap_size: Number of tokens to overlap between chunks
            
        Returns:
            List of DocumentChunk objects
        """
        pass
```

### Concrete Strategy Implementations

#### SectionBasedChunker
```python
class SectionBasedChunker(ChunkingStrategy):
    """Chunks document based on section headings."""
    
    def __init__(self, heading_patterns: List[str] = None):
        """
        Initialize with optional custom heading patterns.
        
        Args:
            heading_patterns: Regex patterns to identify section headings
        """
        self.heading_patterns = heading_patterns or [
            r"^#+\s+.+$",  # Markdown headings
            r"^[A-Z][^.!?]*[.!?]$",  # Potential title lines
            r"^(?:Section|Chapter|Part)\s+\d+",  # Explicit section markers
        ]
    
    def chunk_document(self, document: str, max_chunk_size: int, 
                      overlap_size: int) -> List[DocumentChunk]:
        # Implementation details
        pass
```

#### ParagraphBasedChunker
```python
class ParagraphBasedChunker(ChunkingStrategy):
    """Chunks document based on paragraph breaks."""
    
    def chunk_document(self, document: str, max_chunk_size: int, 
                      overlap_size: int) -> List[DocumentChunk]:
        # Implementation details
        pass
```

#### SemanticBreakChunker
```python
class SemanticBreakChunker(ChunkingStrategy):
    """
    Chunks document based on semantic breaks detected through 
    embedding similarity changes.
    """
    
    def __init__(self, embedding_model: Any):
        """
        Initialize with embedding model for semantic analysis.
        
        Args:
            embedding_model: Model to generate embeddings for text segments
        """
        self.embedding_model = embedding_model
    
    def chunk_document(self, document: str, max_chunk_size: int, 
                      overlap_size: int) -> List[DocumentChunk]:
        # Implementation details
        pass
```

### DocumentChunker (Main Class)
```python
class DocumentChunker:
    """Main class responsible for document chunking."""
    
    def __init__(self, default_strategy: ChunkingStrategy, 
                domain_strategies: Dict[str, ChunkingStrategy] = None,
                token_counter: Callable[[str], int] = None):
        """
        Initialize with strategies and token counter.
        
        Args:
            default_strategy: Default chunking strategy
            domain_strategies: Domain-specific strategies
            token_counter: Function to count tokens in text
        """
        self.default_strategy = default_strategy
        self.domain_strategies = domain_strategies or {}
        self.token_counter = token_counter or self._default_token_counter
    
    def _default_token_counter(self, text: str) -> int:
        """
        Estimate token count based on words/characters.
        For production, use model-specific tokenizers.
        """
        return len(text.split()) * 1.3  # Rough estimate
    
    def chunk_document(self, document: str, domain: str = None, 
                      max_chunk_size: int = 16000,
                      overlap_size: int = 200) -> List[DocumentChunk]:
        """
        Chunk document using appropriate strategy for domain.
        
        Args:
            document: The full text to process
            domain: Domain context (e.g., "medical", "legal")
            max_chunk_size: Maximum tokens per chunk
            overlap_size: Number of tokens to overlap between chunks
            
        Returns:
            List of DocumentChunk objects
        """
        strategy = self.domain_strategies.get(domain, self.default_strategy)
        chunks = strategy.chunk_document(document, max_chunk_size, overlap_size)
        
        # Validate chunks don't exceed token limit
        for chunk in chunks:
            token_count = self.token_counter(chunk.text)
            if token_count > max_chunk_size:
                # Handle oversized chunk (further splitting or logging warning)
                pass
                
        return chunks
```

## Features to Implement

1. **Intelligent Boundary Detection**
   - Identify section headings, paragraph breaks, and semantic shifts
   - Support for domain-specific boundary markers (e.g., legal section numbering)
   - Fallback to simpler strategies when clear boundaries aren't present

2. **Context Preservation**
   - Implement overlapping between chunks to avoid cutting off information
   - Ensure complete sentences at chunk boundaries
   - Track metadata about chunk boundaries for later merging

3. **Token Management**
   - Integrate with LLM-specific tokenizers for accurate token counting
   - Ensure chunks stay within token limits with buffer for prompts
   - Handle edge cases like extremely long paragraphs or sections

4. **Domain Adaptability**
   - Support for domain-specific chunking strategies
   - Configuration-driven approach to customize for different document types
   - Ability to recognize document structure based on content analysis

## Testing Strategy

### Unit Tests

1. **Boundary Detection Tests**
   - Test identification of section headings, paragraphs, and semantic breaks
   - Verify correct handling of different document formats
   - Test edge cases like documents with no clear structure

2. **Chunk Size Tests**
   - Verify chunks stay within token limits
   - Test handling of edge cases like extremely long paragraphs
   - Verify overlap implementation works correctly

3. **Strategy Selection Tests**
   - Test correct strategy selection based on domain
   - Verify fallback to default strategy when needed

### Integration Tests

1. **End-to-End Chunking Tests**
   - Test chunking of complete documents from different domains
   - Verify metadata is correctly populated for downstream components
   - Test with actual token counters from LLM providers

2. **Performance Tests**
   - Measure chunking speed for documents of various sizes
   - Verify memory usage stays within acceptable limits
   - Test with extremely large documents (e.g., 100+ pages)

### Accuracy Tests

1. **Information Preservation Tests**
   - Verify no information is lost during chunking
   - Test reconstruction of original document from chunks
   - Verify context is preserved at chunk boundaries

## Example Usage

```python
# Initialize chunker with strategies
paragraph_chunker = ParagraphBasedChunker()
section_chunker = SectionBasedChunker()

domain_strategies = {
    "legal": section_chunker,
    "medical": section_chunker,
    "general": paragraph_chunker
}

# Create main chunker with tiktoken for OpenAI models
import tiktoken
def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

chunker = DocumentChunker(
    default_strategy=paragraph_chunker,
    domain_strategies=domain_strategies,
    token_counter=count_tokens
)

# Use chunker
with open("large_document.txt", "r") as f:
    document = f.read()

chunks = chunker.chunk_document(
    document=document,
    domain="legal",
    max_chunk_size=15000,  # Leave room for prompt
    overlap_size=200
)

print(f"Document split into {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {len(count_tokens(chunk.text))} tokens")
