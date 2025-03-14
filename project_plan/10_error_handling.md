# Error Handling Service

## Business Description

The Error Handling Service is responsible for managing exceptions and errors throughout the extraction system. It provides a centralized way to detect, categorize, report, and recover from errors, ensuring the system remains robust and resilient. This service is critical for maintaining system stability, providing meaningful error messages, and enabling graceful degradation when components fail.

The Error Handling Service is designed to:
- Detect and categorize different types of errors
- Provide consistent error reporting and logging
- Enable graceful degradation and recovery strategies
- Preserve partial results when possible
- Facilitate debugging and issue resolution

## Dependencies

- **Logging Service**: For detailed error logging
- **Configuration Service**: For error handling configuration settings

## Contracts

### Input
```python
class ErrorContext:
    error: Exception  # The exception that occurred
    component: str  # Component where the error occurred
    operation: str  # Operation being performed
    metadata: Dict[str, Any] = {}  # Additional metadata
    context: Dict[str, Any] = {}  # Error context
```

### Output
```python
class ErrorResult:
    handled: bool  # Whether the error was handled
    recovery_action: str  # Action taken to recover
    should_propagate: bool  # Whether the error should be propagated
    metadata: Dict[str, Any] = {}  # Additional metadata
```

## Core Classes

### ErrorHandler (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type

class ErrorHandler(ABC):
    """Abstract base class for error handlers."""
    
    @abstractmethod
    def can_handle(self, error: Exception, component: str, 
                  operation: str) -> bool:
        """
        Check if handler can handle the error.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            
        Returns:
            True if handler can handle the error
        """
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception, component: str, 
                    operation: str, metadata: Dict[str, Any] = None,
                    context: Dict[str, Any] = None) -> ErrorResult:
        """
        Handle the error.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            metadata: Additional metadata
            context: Error context
            
        Returns:
            Error result
        """
        pass
```

### Concrete Handler Implementations

#### DefaultErrorHandler
```python
from typing import Dict, Any, Optional, Type

class DefaultErrorHandler(ErrorHandler):
    """Default error handler for all errors."""
    
    def __init__(self, logger: LoggingService):
        """
        Initialize with logger.
        
        Args:
            logger: Logging service
        """
        self.logger = logger
    
    def can_handle(self, error: Exception, component: str, 
                  operation: str) -> bool:
        """
        Check if handler can handle the error.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            
        Returns:
            True for all errors
        """
        return True
    
    def handle_error(self, error: Exception, component: str, 
                    operation: str, metadata: Dict[str, Any] = None,
                    context: Dict[str, Any] = None) -> ErrorResult:
        """
        Handle the error by logging it.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            metadata: Additional metadata
            context: Error context
            
        Returns:
            Error result
        """
        # Create error message
        message = f"Error in {component}.{operation}: {str(error)}"
        
        # Add error details to metadata
        merged_metadata = metadata.copy() if metadata else {}
        merged_metadata["component"] = component
        merged_metadata["operation"] = operation
        
        # Log error
        self.logger.log_exception(error, message, merged_metadata, context)
        
        return ErrorResult(
            handled=True,
            recovery_action="logged",
            should_propagate=True,
            metadata={
                "component": component,
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
```

#### RetryableErrorHandler
```python
import time
from typing import Dict, Any, Optional, Type, List

class RetryableErrorHandler(ErrorHandler):
    """Handler for retryable errors."""
    
    def __init__(self, logger: LoggingService,
                retryable_errors: List[Type[Exception]] = None,
                max_retries: int = 3,
                retry_delay: float = 1.0,
                backoff_factor: float = 2.0):
        """
        Initialize with retryable errors and retry settings.
        
        Args:
            logger: Logging service
            retryable_errors: List of retryable exception types
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries (seconds)
            backoff_factor: Factor to increase delay with each retry
        """
        self.logger = logger
        self.retryable_errors = retryable_errors or [
            TimeoutError,
            ConnectionError,
            ConnectionResetError,
            ConnectionRefusedError,
            ConnectionAbortedError
        ]
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
    
    def can_handle(self, error: Exception, component: str, 
                  operation: str) -> bool:
        """
        Check if handler can handle the error.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            
        Returns:
            True if error is retryable
        """
        return any(isinstance(error, error_type) for error_type in self.retryable_errors)
    
    def handle_error(self, error: Exception, component: str, 
                    operation: str, metadata: Dict[str, Any] = None,
                    context: Dict[str, Any] = None) -> ErrorResult:
        """
        Handle the error by retrying the operation.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            metadata: Additional metadata
            context: Error context
            
        Returns:
            Error result
        """
        # Get retry count from metadata
        merged_metadata = metadata.copy() if metadata else {}
        retry_count = merged_metadata.get("retry_count", 0)
        
        # Check if max retries reached
        if retry_count >= self.max_retries:
            # Log error
            message = f"Max retries reached for {component}.{operation}: {str(error)}"
            merged_metadata["component"] = component
            merged_metadata["operation"] = operation
            merged_metadata["max_retries"] = self.max_retries
            
            self.logger.log_error(message, merged_metadata, context)
            
            return ErrorResult(
                handled=True,
                recovery_action="max_retries_reached",
                should_propagate=True,
                metadata={
                    "component": component,
                    "operation": operation,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "retry_count": retry_count,
                    "max_retries": self.max_retries
                }
            )
        
        # Calculate retry delay
        delay = self.retry_delay * (self.backoff_factor ** retry_count)
        
        # Log retry attempt
        message = f"Retrying {component}.{operation} after error: {str(error)}"
        merged_metadata["component"] = component
        merged_metadata["operation"] = operation
        merged_metadata["retry_count"] = retry_count + 1
        merged_metadata["retry_delay"] = delay
        
        self.logger.log_warning(message, merged_metadata, context)
        
        # Sleep before retry
        time.sleep(delay)
        
        return ErrorResult(
            handled=True,
            recovery_action="retry",
            should_propagate=False,
            metadata={
                "component": component,
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "retry_count": retry_count + 1,
                "retry_delay": delay
            }
        )
```

#### FallbackErrorHandler
```python
from typing import Dict, Any, Optional, Type, Callable

class FallbackErrorHandler(ErrorHandler):
    """Handler for errors with fallback options."""
    
    def __init__(self, logger: LoggingService,
                fallback_map: Dict[Type[Exception], Callable] = None):
        """
        Initialize with fallback map.
        
        Args:
            logger: Logging service
            fallback_map: Map of exception types to fallback functions
        """
        self.logger = logger
        self.fallback_map = fallback_map or {}
    
    def can_handle(self, error: Exception, component: str, 
                  operation: str) -> bool:
        """
        Check if handler can handle the error.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            
        Returns:
            True if error has a fallback
        """
        return any(isinstance(error, error_type) for error_type in self.fallback_map.keys())
    
    def handle_error(self, error: Exception, component: str, 
                    operation: str, metadata: Dict[str, Any] = None,
                    context: Dict[str, Any] = None) -> ErrorResult:
        """
        Handle the error by using a fallback.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            metadata: Additional metadata
            context: Error context
            
        Returns:
            Error result
        """
        # Find fallback function
        fallback_func = None
        for error_type, func in self.fallback_map.items():
            if isinstance(error, error_type):
                fallback_func = func
                break
        
        if fallback_func is None:
            # No fallback found
            return ErrorResult(
                handled=False,
                recovery_action="none",
                should_propagate=True,
                metadata={
                    "component": component,
                    "operation": operation,
                    "error_type": type(error).__name__,
                    "error_message": str(error)
                }
            )
        
        # Log fallback
        message = f"Using fallback for {component}.{operation} after error: {str(error)}"
        merged_metadata = metadata.copy() if metadata else {}
        merged_metadata["component"] = component
        merged_metadata["operation"] = operation
        merged_metadata["fallback"] = fallback_func.__name__
        
        self.logger.log_warning(message, merged_metadata, context)
        
        # Call fallback function
        try:
            fallback_func(error, component, operation, metadata, context)
            
            return ErrorResult(
                handled=True,
                recovery_action="fallback",
                should_propagate=False,
                metadata={
                    "component": component,
                    "operation": operation,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "fallback": fallback_func.__name__
                }
            )
        except Exception as fallback_error:
            # Fallback failed
            message = f"Fallback failed for {component}.{operation}: {str(fallback_error)}"
            merged_metadata["fallback_error"] = str(fallback_error)
            
            self.logger.log_error(message, merged_metadata, context)
            
            return ErrorResult(
                handled=False,
                recovery_action="fallback_failed",
                should_propagate=True,
                metadata={
                    "component": component,
                    "operation": operation,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "fallback": fallback_func.__name__,
                    "fallback_error": str(fallback_error)
                }
            )
```

### ErrorHandlingService
```python
from typing import Dict, Any, List, Optional, Type

class ErrorHandlingService:
    """Service for handling errors."""
    
    def __init__(self, logger: LoggingService,
                handlers: List[ErrorHandler] = None):
        """
        Initialize with logger and handlers.
        
        Args:
            logger: Logging service
            handlers: List of error handlers
        """
        self.logger = logger
        
        # Create default handler
        default_handler = DefaultErrorHandler(logger)
        
        # Add handlers
        self.handlers = handlers or []
        
        # Ensure default handler is last
        if default_handler not in self.handlers:
            self.handlers.append(default_handler)
    
    def add_handler(self, handler: ErrorHandler) -> None:
        """
        Add an error handler.
        
        Args:
            handler: Error handler to add
        """
        # Add before default handler
        if self.handlers:
            self.handlers.insert(-1, handler)
        else:
            self.handlers.append(handler)
    
    def handle_error(self, error: Exception, component: str, 
                    operation: str, metadata: Dict[str, Any] = None,
                    context: Dict[str, Any] = None) -> ErrorResult:
        """
        Handle an error.
        
        Args:
            error: The exception that occurred
            component: Component where the error occurred
            operation: Operation being performed
            metadata: Additional metadata
            context: Error context
            
        Returns:
            Error result
        """
        # Find handler for error
        for handler in self.handlers:
            if handler.can_handle(error, component, operation):
                result = handler.handle_error(
                    error, component, operation, metadata, context
                )
                
                if result.handled:
                    return result
        
        # No handler found
        return ErrorResult(
            handled=False,
            recovery_action="none",
            should_propagate=True,
            metadata={
                "component": component,
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
    
    def handle_chunking_error(self, error: Exception, 
                            document: str) -> None:
        """
        Handle chunking error.
        
        Args:
            error: The exception that occurred
            document: Document being chunked
        """
        metadata = {
            "document_length": len(document)
        }
        
        self.handle_error(error, "chunker", "chunk_document", metadata)
    
    def handle_processing_error(self, error: Exception, 
                              chunks: List[Any]) -> None:
        """
        Handle processing error.
        
        Args:
            error: The exception that occurred
            chunks: Chunks being processed
        """
        metadata = {
            "chunk_count": len(chunks)
        }
        
        self.handle_error(error, "processor", "process_chunks", metadata)
    
    def handle_extraction_error(self, error: Exception, 
                              chunk: Any, fields: List[str]) -> None:
        """
        Handle extraction error.
        
        Args:
            error: The exception that occurred
            chunk: Chunk being processed
            fields: Fields being extracted
        """
        metadata = {
            "chunk_index": chunk.index,
            "fields": fields
        }
        
        self.handle_error(error, "extractor", "extract_fields", metadata)
    
    def handle_normalization_error(self, error: Exception, 
                                 chunks: List[Any]) -> None:
        """
        Handle normalization error.
        
        Args:
            error: The exception that occurred
            chunks: Chunks being normalized
        """
        metadata = {
            "chunk_count": len(chunks)
        }
        
        self.handle_error(error, "normalizer", "normalize", metadata)
    
    def handle_merging_error(self, error: Exception, 
                           chunks: List[Any]) -> None:
        """
        Handle merging error.
        
        Args:
            error: The exception that occurred
            chunks: Chunks being merged
        """
        metadata = {
            "chunk_count": len(chunks)
        }
        
        self.handle_error(error, "merger", "merge_results", metadata)
    
    def handle_formatting_error(self, error: Exception, 
                              result: Any) -> None:
        """
        Handle formatting error.
        
        Args:
            error: The exception that occurred
            result: Result being formatted
        """
        metadata = {
            "result_type": type(result).__name__
        }
        
        self.handle_error(error, "formatter", "format_output", metadata)
    
    def handle_configuration_error(self, error: Exception, 
                                 config_key: str) -> None:
        """
        Handle configuration error.
        
        Args:
            error: The exception that occurred
            config_key: Configuration key
        """
        metadata = {
            "config_key": config_key
        }
        
        self.handle_error(error, "configuration", "get_config", metadata)
    
    def handle_pipeline_error(self, error: Exception, 
                            request: Any) -> None:
        """
        Handle pipeline error.
        
        Args:
            error: The exception that occurred
            request: Extraction request
        """
        metadata = {
            "request_type": type(request).__name__
        }
        
        self.handle_error(error, "pipeline", "process_document", metadata)
    
    def handle_service_error(self, error: Exception, 
                           request: Any) -> None:
        """
        Handle service error.
        
        Args:
            error: The exception that occurred
            request: Extraction request
        """
        metadata = {
            "request_type": type(request).__name__
        }
        
        self.handle_error(error, "service", "extract", metadata)
```

## Features to Implement

1. **Error Detection and Categorization**
   - Exception type-based categorization
   - Error severity classification
   - Component-specific error handling
   - Custom error types for domain-specific errors

2. **Recovery Strategies**
   - Retry with exponential backoff
   - Fallback mechanisms
   - Graceful degradation
   - Partial result preservation

3. **Error Reporting**
   - Detailed error logging
   - Error aggregation and analysis
   - Error notification and alerting
   - Error tracking and monitoring

4. **Debugging Support**
   - Stack trace preservation
   - Context capture
   - Error reproduction information
   - Troubleshooting guidance

5. **Error Prevention**
   - Input validation
   - Precondition checking
   - Resource monitoring
   - Circuit breaker pattern

## Testing Strategy

### Unit Tests

1. **Handler Tests**
   - Test each handler independently
   - Verify correct error categorization
   - Test recovery strategies
   - Verify error reporting

2. **Service Tests**
   - Test error handling service with different errors
   - Verify handler selection logic
   - Test component-specific error handling
   - Verify error result generation

3. **Recovery Tests**
   - Test retry mechanism
   - Verify fallback functionality
   - Test graceful degradation
   - Verify partial result preservation

### Integration Tests

1. **Component Integration Tests**
   - Test error handling with other components
   - Verify error propagation
   - Test recovery in integrated environment
   - Verify logging integration

2. **System Tests**
   - Test error handling in complete system
   - Verify system stability under error conditions
   - Test error reporting and monitoring
   - Verify user experience during errors

### Stress Tests

1. **Error Flood Tests**
   - Test handling of multiple simultaneous errors
   - Verify system stability under high error rates
   - Test resource usage during error handling
   - Verify recovery from cascading failures

2. **Resource Exhaustion Tests**
   - Test handling of out-of-memory errors
   - Verify behavior with network failures
   - Test with disk space limitations
   - Verify handling of CPU overload

## Example Usage

```python
from typing import Dict, Any, List

def main():
    # Initialize logger
    logger = LoggingService([ConsoleLogHandler()])
    
    # Initialize error handlers
    retryable_handler = RetryableErrorHandler(
        logger=logger,
        max_retries=3,
        retry_delay=1.0,
        backoff_factor=2.0
    )
    
    # Define fallback functions
    def chunking_fallback(error, component, operation, metadata, context):
        # Fallback to simpler chunking strategy
        print("Using simpler chunking strategy")
    
    def extraction_fallback(error, component, operation, metadata, context):
        # Fallback to basic extraction
        print("Using basic extraction")
    
    # Initialize fallback handler
    fallback_handler = FallbackErrorHandler(
        logger=logger,
        fallback_map={
            ValueError: chunking_fallback,
            KeyError: extraction_fallback
        }
    )
    
    # Initialize error handling service
    error_handler = ErrorHandlingService(
        logger=logger,
        handlers=[retryable_handler, fallback_handler]
    )
    
    # Example 1: Handle retryable error
    try:
        # Simulate connection error
        raise ConnectionError("Failed to connect to LLM API")
    except Exception as e:
        result = error_handler.handle_error(
            error=e,
            component="processor",
            operation="process_chunk",
            metadata={"chunk_id": "chunk1"}
        )
        
        print(f"Handled: {result.handled}")
        print(f"Recovery action: {result.recovery_action}")
        print(f"Should propagate: {result.should_propagate}")
    
    # Example 2: Handle error with fallback
    try:
        # Simulate value error
        raise ValueError("Invalid chunk size")
    except Exception as e:
        result = error_handler.handle_error(
            error=e,
            component="chunker",
            operation="chunk_document",
            metadata={"document_id": "doc1"}
        )
        
        print(f"Handled: {result.handled}")
        print(f"Recovery action: {result.recovery_action}")
        print(f"Should propagate: {result.should_propagate}")
    
    # Example 3: Handle component-specific error
    try:
        # Simulate extraction error
        raise KeyError("Field not found")
    except Exception as e:
        # Use component-specific handler
        error_handler.handle_extraction_error(
            error=e,
            chunk={"index": 1},
            fields=["patient_name", "date_of_birth"]
        )

# Run the function
main()
```

## Example Error Handling Flow

1. **Error Detection**
   - An exception occurs during document chunking
   - The exception is caught and passed to the error handling service

2. **Handler Selection**
   - The error handling service iterates through its handlers
   - Each handler checks if it can handle the error
   - The first handler that can handle the error is selected

3. **Error Handling**
   - The selected handler processes the error
   - It may implement a recovery strategy (retry, fallback, etc.)
   - It logs the error with appropriate context

4. **Result Generation**
   - The handler generates an error result
   - The result indicates whether the error was handled
   - It specifies the recovery action taken
   - It indicates whether the error should be propagated

5. **Error Propagation**
   - If the error should be propagated, it is re-thrown
   - Otherwise, the system continues operation
   - Partial results may be preserved and returned

This flow ensures that errors are handled consistently and appropriately throughout the system, with the right balance between recovery attempts and error propagation.
