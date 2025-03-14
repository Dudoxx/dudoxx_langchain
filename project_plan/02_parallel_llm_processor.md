# Parallel LLM Processor

## Business Description

The Parallel LLM Processor is responsible for managing concurrent LLM requests to process document chunks in parallel. This component leverages up to 20 parallel LLM requests to dramatically speed up processing. Once the document is chunked, each chunk is sent to the LLM simultaneously (up to the concurrency limit) rather than one after the other. This parallelization takes advantage of Dudoxx's infrastructure to handle multiple LLM calls at once, effectively cutting down overall latency.

The Parallel LLM Processor is designed to:
- Manage a pool of concurrent LLM requests (up to 20)
- Distribute chunks to available LLM instances
- Track the status of each request
- Handle rate limiting and retries
- Optimize throughput while maintaining accuracy

## Dependencies

- **Document Chunker**: Provides the chunks to be processed
- **Field Extractor**: Provides the prompts and parsing logic for each chunk
- **Configuration Service**: For LLM-specific settings and rate limits
- **Logging Service**: For tracking request status and performance metrics
- **Error Handling Service**: For managing exceptions during LLM processing

## Contracts

### Input
```python
class ProcessingRequest:
    chunks: List[DocumentChunk]  # Chunks to process
    prompt_template: str  # Template for LLM prompts
    fields: List[str]  # Fields to extract
    model_name: str  # LLM model to use
    max_concurrency: int = 20  # Maximum concurrent requests
    timeout: int = 60  # Timeout in seconds per request
    retry_attempts: int = 3  # Number of retry attempts
```

### Output
```python
class ProcessedChunk:
    chunk: DocumentChunk  # Original chunk
    result: Dict[str, Any]  # Extracted data
    processing_metadata: Dict[str, Any]  # Contains:
        # - processing_time: float  # Time taken to process
        # - token_count: int  # Tokens used
        # - model_name: str  # Model used
        # - attempt_count: int  # Number of attempts
```

## Core Classes

### LLMClient (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMClient(ABC):
    """Abstract base class for LLM API clients."""
    
    @abstractmethod
    async def process_prompt(self, prompt: str, 
                           model_name: str,
                           temperature: float = 0.0,
                           max_tokens: Optional[int] = None,
                           timeout: int = 60) -> Dict[str, Any]:
        """
        Send prompt to LLM and get response.
        
        Args:
            prompt: The prompt to send to the LLM
            model_name: Name of the model to use
            temperature: Temperature parameter (0.0 for deterministic)
            max_tokens: Maximum tokens in response
            timeout: Timeout in seconds
            
        Returns:
            Dictionary containing LLM response and metadata
        """
        pass
```

### Concrete LLM Client Implementations

#### OpenAICompatibleClient
```python
import openai
from openai import AsyncOpenAI
import time
from typing import Dict, Any, Optional

class OpenAICompatibleClient(LLMClient):
    """Client for OpenAI-compatible APIs (including Dudoxx)."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize with API key and optional base URL.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API (None for OpenAI default)
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def process_prompt(self, prompt: str, 
                           model_name: str,
                           temperature: float = 0.0,
                           max_tokens: Optional[int] = None,
                           timeout: int = 60) -> Dict[str, Any]:
        """
        Send prompt to OpenAI-compatible LLM and get response.
        
        Args:
            prompt: The prompt to send to the LLM
            model_name: Name of the model to use
            temperature: Temperature parameter (0.0 for deterministic)
            max_tokens: Maximum tokens in response
            timeout: Timeout in seconds
            
        Returns:
            Dictionary containing LLM response and metadata
        """
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            
            processing_time = time.time() - start_time
            
            return {
                "content": response.choices[0].message.content,
                "metadata": {
                    "processing_time": processing_time,
                    "model_name": model_name,
                    "token_usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            }
        except Exception as e:
            processing_time = time.time() - start_time
            
            return {
                "error": str(e),
                "metadata": {
                    "processing_time": processing_time,
                    "model_name": model_name
                }
            }
```

### RequestTracker
```python
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class RequestStatus(Enum):
    """Enum for request status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class RequestTracker:
    """Tracks status of parallel requests."""
    
    def __init__(self):
        """Initialize request tracker."""
        self.requests = {}
        self.start_time = time.time()
    
    def add_request(self, request_id: str, chunk_index: int) -> None:
        """
        Add a new request to track.
        
        Args:
            request_id: Unique identifier for request
            chunk_index: Index of chunk being processed
        """
        self.requests[request_id] = {
            "status": RequestStatus.PENDING,
            "chunk_index": chunk_index,
            "start_time": None,
            "end_time": None,
            "duration": None,
            "attempt": 1,
            "error": None
        }
    
    def update_status(self, request_id: str, status: RequestStatus, 
                     error: Optional[str] = None) -> None:
        """
        Update status of a request.
        
        Args:
            request_id: Unique identifier for request
            status: New status
            error: Error message if failed
        """
        if request_id not in self.requests:
            return
            
        self.requests[request_id]["status"] = status
        
        if status == RequestStatus.IN_PROGRESS and not self.requests[request_id]["start_time"]:
            self.requests[request_id]["start_time"] = time.time()
            
        if status in [RequestStatus.COMPLETED, RequestStatus.FAILED]:
            self.requests[request_id]["end_time"] = time.time()
            self.requests[request_id]["duration"] = (
                self.requests[request_id]["end_time"] - 
                self.requests[request_id]["start_time"]
            )
            
        if status == RequestStatus.FAILED:
            self.requests[request_id]["error"] = error
            
        if status == RequestStatus.RETRYING:
            self.requests[request_id]["attempt"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all requests.
        
        Returns:
            Dictionary with request statistics
        """
        total = len(self.requests)
        completed = sum(1 for r in self.requests.values() if r["status"] == RequestStatus.COMPLETED)
        failed = sum(1 for r in self.requests.values() if r["status"] == RequestStatus.FAILED)
        in_progress = sum(1 for r in self.requests.values() if r["status"] == RequestStatus.IN_PROGRESS)
        pending = sum(1 for r in self.requests.values() if r["status"] == RequestStatus.PENDING)
        retrying = sum(1 for r in self.requests.values() if r["status"] == RequestStatus.RETRYING)
        
        durations = [r["duration"] for r in self.requests.values() if r["duration"] is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": pending,
            "retrying": retrying,
            "average_duration": avg_duration,
            "total_duration": time.time() - self.start_time
        }
```

### ParallelProcessor
```python
import asyncio
from typing import List, Dict, Any, Callable, Coroutine
import uuid

class ParallelProcessor:
    """Manages parallel processing of chunks."""
    
    def __init__(self, llm_client: LLMClient, max_concurrency: int = 20):
        """
        Initialize with LLM client and concurrency limit.
        
        Args:
            llm_client: Client for LLM API
            max_concurrency: Maximum concurrent requests
        """
        self.llm_client = llm_client
        self.max_concurrency = max_concurrency
        self.request_tracker = RequestTracker()
        self.semaphore = asyncio.Semaphore(max_concurrency)
    
    async def _process_single_chunk(self, chunk: DocumentChunk, 
                                  processor_func: Callable[[DocumentChunk], Coroutine],
                                  request_id: str) -> ProcessedChunk:
        """
        Process a single chunk with rate limiting.
        
        Args:
            chunk: Document chunk to process
            processor_func: Function to process chunk
            request_id: Unique identifier for request
            
        Returns:
            Processed chunk
        """
        async with self.semaphore:
            self.request_tracker.update_status(request_id, RequestStatus.IN_PROGRESS)
            
            try:
                result = await processor_func(chunk)
                self.request_tracker.update_status(request_id, RequestStatus.COMPLETED)
                return result
            except Exception as e:
                self.request_tracker.update_status(request_id, RequestStatus.FAILED, str(e))
                raise
    
    async def process_chunks(self, chunks: List[DocumentChunk], 
                           processor_func: Callable[[DocumentChunk], Coroutine],
                           retry_attempts: int = 3) -> List[ProcessedChunk]:
        """
        Process multiple chunks in parallel.
        
        Args:
            chunks: List of document chunks
            processor_func: Function to process each chunk
            retry_attempts: Number of retry attempts
            
        Returns:
            List of processed chunks
        """
        tasks = []
        
        for i, chunk in enumerate(chunks):
            request_id = str(uuid.uuid4())
            self.request_tracker.add_request(request_id, i)
            
            task = asyncio.create_task(
                self._process_with_retry(
                    chunk, processor_func, request_id, retry_attempts
                )
            )
            tasks.append(task)
        
        # Process all chunks and gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        processed_chunks = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Log exception
                continue
            processed_chunks.append(result)
        
        return processed_chunks
    
    async def _process_with_retry(self, chunk: DocumentChunk,
                                processor_func: Callable[[DocumentChunk], Coroutine],
                                request_id: str,
                                retry_attempts: int) -> ProcessedChunk:
        """
        Process chunk with retry logic.
        
        Args:
            chunk: Document chunk to process
            processor_func: Function to process chunk
            request_id: Unique identifier for request
            retry_attempts: Number of retry attempts
            
        Returns:
            Processed chunk
        """
        attempts = 0
        last_exception = None
        
        while attempts < retry_attempts:
            try:
                return await self._process_single_chunk(chunk, processor_func, request_id)
            except Exception as e:
                attempts += 1
                last_exception = e
                
                if attempts < retry_attempts:
                    self.request_tracker.update_status(request_id, RequestStatus.RETRYING)
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempts)
        
        # If we get here, all retries failed
        raise last_exception
```

## Features to Implement

1. **Concurrent Request Management**
   - Implement semaphore-based concurrency control
   - Support for configurable maximum concurrent requests
   - Queue management for chunks exceeding concurrency limit

2. **LLM Provider Integration**
   - Support for OpenAI-compatible APIs (including Dudoxx)
   - Adapter pattern for different LLM providers
   - Configuration-driven model selection

3. **Request Tracking and Monitoring**
   - Real-time tracking of request status
   - Performance metrics collection
   - Detailed logging of request lifecycle

4. **Error Handling and Resilience**
   - Automatic retry with exponential backoff
   - Circuit breaker pattern for failing endpoints
   - Graceful degradation options

5. **Throughput Optimization**
   - Dynamic concurrency adjustment based on rate limits
   - Batch processing for efficiency
   - Priority queue for important chunks

## Testing Strategy

### Unit Tests

1. **Concurrency Control Tests**
   - Verify semaphore correctly limits concurrent requests
   - Test queue behavior when concurrency limit is reached
   - Verify tasks are properly distributed

2. **LLM Client Tests**
   - Test API client with mock responses
   - Verify correct handling of different response formats
   - Test error handling and retry logic

3. **Request Tracking Tests**
   - Verify correct status updates
   - Test summary statistics calculation
   - Verify timing measurements

### Integration Tests

1. **End-to-End Processing Tests**
   - Test processing of multiple chunks
   - Verify correct handling of results
   - Test with actual LLM API (using test account)

2. **Performance Tests**
   - Measure throughput with varying concurrency settings
   - Test behavior under rate limiting conditions
   - Verify memory usage with large numbers of chunks

### Stress Tests

1. **Rate Limit Handling**
   - Test behavior when hitting API rate limits
   - Verify backoff and retry mechanisms
   - Measure recovery time after rate limit errors

2. **Error Recovery Tests**
   - Simulate random failures and verify recovery
   - Test behavior with unreliable network conditions
   - Verify system can handle partial failures

## Example Usage

```python
import asyncio
from typing import List, Dict, Any

async def main():
    # Initialize LLM client
    llm_client = OpenAICompatibleClient(
        api_key="your-api-key",
        base_url="https://api.dudoxx.ai/v1"  # Example for Dudoxx
    )
    
    # Initialize parallel processor
    processor = ParallelProcessor(
        llm_client=llm_client,
        max_concurrency=20
    )
    
    # Define processing function
    async def process_chunk(chunk: DocumentChunk) -> ProcessedChunk:
        prompt = f"Extract the following fields from the text: {', '.join(fields)}\n\nText: {chunk.text}"
        
        response = await llm_client.process_prompt(
            prompt=prompt,
            model_name="dudoxx-extract-1",
            temperature=0.0
        )
        
        # Parse response (simplified)
        extracted_data = json.loads(response["content"])
        
        return ProcessedChunk(
            chunk=chunk,
            result=extracted_data,
            processing_metadata=response["metadata"]
        )
    
    # Process chunks
    chunks = chunker.chunk_document(document)
    fields = ["patient_name", "date_of_birth", "diagnosis"]
    
    processed_chunks = await processor.process_chunks(
        chunks=chunks,
        processor_func=process_chunk,
        retry_attempts=3
    )
    
    # Get processing summary
    summary = processor.request_tracker.get_summary()
    print(f"Processed {summary['completed']}/{summary['total']} chunks in {summary['total_duration']:.2f} seconds")
    print(f"Average processing time: {summary['average_duration']:.2f} seconds per chunk")
    
    return processed_chunks

# Run the async function
processed_chunks = asyncio.run(main())
