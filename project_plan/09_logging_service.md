# Logging Service

## Business Description

The Logging Service is responsible for tracking and recording events, metrics, and errors throughout the extraction system. It provides a centralized way to capture information about the system's operation, enabling monitoring, debugging, and performance analysis. This service is critical for understanding system behavior, diagnosing issues, and optimizing performance.

The Logging Service is designed to:
- Capture events at different severity levels (debug, info, warning, error)
- Record structured metadata along with log messages
- Support multiple output destinations (console, file, external services)
- Enable contextual logging with correlation IDs
- Provide performance metrics and timing information

## Dependencies

- **Configuration Service**: For logging configuration settings
- **Error Handling Service**: For detailed error logging

## Contracts

### Input
```python
class LogEntry:
    level: str  # Log level (debug, info, warning, error)
    message: str  # Log message
    metadata: Dict[str, Any] = {}  # Additional metadata
    timestamp: Optional[datetime] = None  # Timestamp (defaults to now)
    context: Optional[Dict[str, Any]] = None  # Logging context
```

### Output
```python
class LogResult:
    success: bool  # Whether logging was successful
    log_id: Optional[str] = None  # Unique identifier for log entry
    metadata: Dict[str, Any] = {}  # Additional metadata
```

## Core Classes

### LogHandler (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class LogHandler(ABC):
    """Abstract base class for log handlers."""
    
    @abstractmethod
    def log(self, level: str, message: str, 
           metadata: Dict[str, Any] = None,
           timestamp: Optional[datetime] = None,
           context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a message.
        
        Args:
            level: Log level
            message: Log message
            metadata: Additional metadata
            timestamp: Timestamp (defaults to now)
            context: Logging context
            
        Returns:
            True if logging was successful
        """
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """
        Flush any buffered log entries.
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the handler and release resources.
        """
        pass
```

### Concrete Handler Implementations

#### ConsoleLogHandler
```python
import sys
import json
from typing import Dict, Any, Optional, TextIO
from datetime import datetime

class ConsoleLogHandler(LogHandler):
    """Logs to console (stdout/stderr)."""
    
    def __init__(self, output: TextIO = sys.stdout,
                use_colors: bool = True,
                min_level: str = "debug"):
        """
        Initialize with output stream.
        
        Args:
            output: Output stream (stdout or stderr)
            use_colors: Whether to use colors in output
            min_level: Minimum log level to output
        """
        self.output = output
        self.use_colors = use_colors
        self.min_level = min_level
        
        # Level to numeric value mapping
        self.level_map = {
            "debug": 10,
            "info": 20,
            "warning": 30,
            "error": 40,
            "critical": 50
        }
        
        # ANSI color codes
        self.colors = {
            "debug": "\033[36m",  # Cyan
            "info": "\033[32m",   # Green
            "warning": "\033[33m", # Yellow
            "error": "\033[31m",  # Red
            "critical": "\033[35m", # Magenta
            "reset": "\033[0m"
        }
    
    def log(self, level: str, message: str, 
           metadata: Dict[str, Any] = None,
           timestamp: Optional[datetime] = None,
           context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a message to console.
        
        Args:
            level: Log level
            message: Log message
            metadata: Additional metadata
            timestamp: Timestamp (defaults to now)
            context: Logging context
            
        Returns:
            True if logging was successful
        """
        # Check if level is high enough
        if self.level_map.get(level.lower(), 0) < self.level_map.get(self.min_level, 0):
            return True
            
        # Get timestamp
        if timestamp is None:
            timestamp = datetime.now()
            
        # Format timestamp
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Format level
        level_str = level.upper()
        
        # Format context
        context_str = ""
        if context:
            context_id = context.get("correlation_id")
            if context_id:
                context_str = f"[{context_id}] "
        
        # Format metadata
        metadata_str = ""
        if metadata:
            metadata_str = " " + json.dumps(metadata)
        
        # Format log entry
        if self.use_colors and level.lower() in self.colors:
            color = self.colors[level.lower()]
            reset = self.colors["reset"]
            log_entry = f"{timestamp_str} {color}{level_str}{reset} {context_str}{message}{metadata_str}\n"
        else:
            log_entry = f"{timestamp_str} {level_str} {context_str}{message}{metadata_str}\n"
        
        # Write to output
        try:
            self.output.write(log_entry)
            self.output.flush()
            return True
        except Exception:
            return False
    
    def flush(self) -> None:
        """
        Flush the output stream.
        """
        self.output.flush()
    
    def close(self) -> None:
        """
        Close the handler.
        """
        # Don't close stdout/stderr
        pass
```

#### FileLogHandler
```python
import os
import json
from typing import Dict, Any, Optional, TextIO
from datetime import datetime

class FileLogHandler(LogHandler):
    """Logs to file."""
    
    def __init__(self, file_path: str,
                min_level: str = "debug",
                max_size: int = 10 * 1024 * 1024,  # 10 MB
                backup_count: int = 5):
        """
        Initialize with file path.
        
        Args:
            file_path: Path to log file
            min_level: Minimum log level to output
            max_size: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        self.file_path = file_path
        self.min_level = min_level
        self.max_size = max_size
        self.backup_count = backup_count
        
        # Level to numeric value mapping
        self.level_map = {
            "debug": 10,
            "info": 20,
            "warning": 30,
            "error": 40,
            "critical": 50
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Open file
        self.file = open(file_path, "a", encoding="utf-8")
    
    def log(self, level: str, message: str, 
           metadata: Dict[str, Any] = None,
           timestamp: Optional[datetime] = None,
           context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a message to file.
        
        Args:
            level: Log level
            message: Log message
            metadata: Additional metadata
            timestamp: Timestamp (defaults to now)
            context: Logging context
            
        Returns:
            True if logging was successful
        """
        # Check if level is high enough
        if self.level_map.get(level.lower(), 0) < self.level_map.get(self.min_level, 0):
            return True
            
        # Check if file needs rotation
        if self.file.tell() > self.max_size:
            self._rotate_file()
            
        # Get timestamp
        if timestamp is None:
            timestamp = datetime.now()
            
        # Format timestamp
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Format level
        level_str = level.upper()
        
        # Format context
        context_str = ""
        if context:
            context_id = context.get("correlation_id")
            if context_id:
                context_str = f"[{context_id}] "
        
        # Format metadata
        metadata_str = ""
        if metadata:
            metadata_str = " " + json.dumps(metadata)
        
        # Format log entry
        log_entry = f"{timestamp_str} {level_str} {context_str}{message}{metadata_str}\n"
        
        # Write to file
        try:
            self.file.write(log_entry)
            self.file.flush()
            return True
        except Exception:
            return False
    
    def flush(self) -> None:
        """
        Flush the file.
        """
        self.file.flush()
    
    def close(self) -> None:
        """
        Close the file.
        """
        self.file.close()
    
    def _rotate_file(self) -> None:
        """
        Rotate log file.
        """
        # Close current file
        self.file.close()
        
        # Rotate backup files
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.file_path}.{i}"
            dst = f"{self.file_path}.{i + 1}"
            
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
        
        # Rename current file
        if os.path.exists(self.file_path):
            dst = f"{self.file_path}.1"
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(self.file_path, dst)
        
        # Open new file
        self.file = open(self.file_path, "a", encoding="utf-8")
```

#### JsonLogHandler
```python
import json
import os
from typing import Dict, Any, Optional, TextIO
from datetime import datetime

class JsonLogHandler(LogHandler):
    """Logs to file in JSON format."""
    
    def __init__(self, file_path: str,
                min_level: str = "debug",
                max_size: int = 10 * 1024 * 1024,  # 10 MB
                backup_count: int = 5):
        """
        Initialize with file path.
        
        Args:
            file_path: Path to log file
            min_level: Minimum log level to output
            max_size: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        self.file_path = file_path
        self.min_level = min_level
        self.max_size = max_size
        self.backup_count = backup_count
        
        # Level to numeric value mapping
        self.level_map = {
            "debug": 10,
            "info": 20,
            "warning": 30,
            "error": 40,
            "critical": 50
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Open file
        self.file = open(file_path, "a", encoding="utf-8")
    
    def log(self, level: str, message: str, 
           metadata: Dict[str, Any] = None,
           timestamp: Optional[datetime] = None,
           context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a message to file in JSON format.
        
        Args:
            level: Log level
            message: Log message
            metadata: Additional metadata
            timestamp: Timestamp (defaults to now)
            context: Logging context
            
        Returns:
            True if logging was successful
        """
        # Check if level is high enough
        if self.level_map.get(level.lower(), 0) < self.level_map.get(self.min_level, 0):
            return True
            
        # Check if file needs rotation
        if self.file.tell() > self.max_size:
            self._rotate_file()
            
        # Get timestamp
        if timestamp is None:
            timestamp = datetime.now()
            
        # Create log entry
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "level": level.upper(),
            "message": message
        }
        
        # Add context
        if context:
            log_entry["context"] = context
        
        # Add metadata
        if metadata:
            log_entry["metadata"] = metadata
        
        # Write to file
        try:
            self.file.write(json.dumps(log_entry) + "\n")
            self.file.flush()
            return True
        except Exception:
            return False
    
    def flush(self) -> None:
        """
        Flush the file.
        """
        self.file.flush()
    
    def close(self) -> None:
        """
        Close the file.
        """
        self.file.close()
    
    def _rotate_file(self) -> None:
        """
        Rotate log file.
        """
        # Close current file
        self.file.close()
        
        # Rotate backup files
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.file_path}.{i}"
            dst = f"{self.file_path}.{i + 1}"
            
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
        
        # Rename current file
        if os.path.exists(self.file_path):
            dst = f"{self.file_path}.1"
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(self.file_path, dst)
        
        # Open new file
        self.file = open(self.file_path, "a", encoding="utf-8")
```

### LoggingService
```python
import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

class LoggingService:
    """Service for logging events and metrics."""
    
    def __init__(self, handlers: List[LogHandler] = None,
                context: Dict[str, Any] = None):
        """
        Initialize with handlers and context.
        
        Args:
            handlers: List of log handlers
            context: Global logging context
        """
        self.handlers = handlers or []
        self.context = context or {}
        
        # Generate correlation ID if not provided
        if "correlation_id" not in self.context:
            self.context["correlation_id"] = str(uuid.uuid4())
    
    def add_handler(self, handler: LogHandler) -> None:
        """
        Add a log handler.
        
        Args:
            handler: Log handler to add
        """
        self.handlers.append(handler)
    
    def remove_handler(self, handler: LogHandler) -> None:
        """
        Remove a log handler.
        
        Args:
            handler: Log handler to remove
        """
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Set context value.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
    
    def clear_context(self) -> None:
        """
        Clear all context values.
        """
        self.context = {}
        
        # Generate new correlation ID
        self.context["correlation_id"] = str(uuid.uuid4())
    
    def log(self, level: str, message: str, 
           metadata: Dict[str, Any] = None,
           timestamp: Optional[datetime] = None,
           context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log a message to all handlers.
        
        Args:
            level: Log level
            message: Log message
            metadata: Additional metadata
            timestamp: Timestamp (defaults to now)
            context: Additional context (merged with global context)
            
        Returns:
            Log result
        """
        # Get timestamp
        if timestamp is None:
            timestamp = datetime.now()
            
        # Merge context
        merged_context = self.context.copy()
        if context:
            merged_context.update(context)
            
        # Generate log ID
        log_id = str(uuid.uuid4())
        
        # Add log ID to metadata
        merged_metadata = metadata.copy() if metadata else {}
        merged_metadata["log_id"] = log_id
        
        # Log to all handlers
        success = True
        for handler in self.handlers:
            if not handler.log(level, message, merged_metadata, timestamp, merged_context):
                success = False
        
        return LogResult(
            success=success,
            log_id=log_id,
            metadata={
                "timestamp": timestamp.isoformat(),
                "level": level,
                "context": merged_context
            }
        )
    
    def log_debug(self, message: str, metadata: Dict[str, Any] = None,
                context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log a debug message.
        
        Args:
            message: Log message
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        return self.log("debug", message, metadata, None, context)
    
    def log_info(self, message: str, metadata: Dict[str, Any] = None,
               context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log an info message.
        
        Args:
            message: Log message
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        return self.log("info", message, metadata, None, context)
    
    def log_warning(self, message: str, metadata: Dict[str, Any] = None,
                  context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log a warning message.
        
        Args:
            message: Log message
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        return self.log("warning", message, metadata, None, context)
    
    def log_error(self, message: str, metadata: Dict[str, Any] = None,
                context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log an error message.
        
        Args:
            message: Log message
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        return self.log("error", message, metadata, None, context)
    
    def log_critical(self, message: str, metadata: Dict[str, Any] = None,
                   context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log a critical message.
        
        Args:
            message: Log message
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        return self.log("critical", message, metadata, None, context)
    
    def log_exception(self, exception: Exception, message: str = None,
                    metadata: Dict[str, Any] = None,
                    context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log an exception.
        
        Args:
            exception: Exception to log
            message: Optional message
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        # Get exception details
        exc_type = type(exception).__name__
        exc_message = str(exception)
        
        # Create message if not provided
        if message is None:
            message = f"Exception: {exc_type}: {exc_message}"
        
        # Add exception details to metadata
        merged_metadata = metadata.copy() if metadata else {}
        merged_metadata["exception"] = {
            "type": exc_type,
            "message": exc_message
        }
        
        # Add traceback if available
        import traceback
        merged_metadata["exception"]["traceback"] = traceback.format_exc()
        
        return self.log("error", message, merged_metadata, None, context)
    
    def log_performance(self, operation: str, duration: float,
                      metadata: Dict[str, Any] = None,
                      context: Optional[Dict[str, Any]] = None) -> LogResult:
        """
        Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Log result
        """
        # Create message
        message = f"Performance: {operation} took {duration:.6f} seconds"
        
        # Add performance details to metadata
        merged_metadata = metadata.copy() if metadata else {}
        merged_metadata["performance"] = {
            "operation": operation,
            "duration": duration
        }
        
        return self.log("info", message, merged_metadata, None, context)
    
    def timed_operation(self, operation: str,
                      metadata: Dict[str, Any] = None,
                      context: Optional[Dict[str, Any]] = None):
        """
        Context manager for timing operations.
        
        Args:
            operation: Operation name
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            Context manager
        """
        return TimedOperation(self, operation, metadata, context)
    
    def flush(self) -> None:
        """
        Flush all handlers.
        """
        for handler in self.handlers:
            handler.flush()
    
    def close(self) -> None:
        """
        Close all handlers.
        """
        for handler in self.handlers:
            handler.close()
```

### TimedOperation
```python
import time
from typing import Dict, Any, Optional

class TimedOperation:
    """Context manager for timing operations."""
    
    def __init__(self, logger: LoggingService, operation: str,
                metadata: Dict[str, Any] = None,
                context: Optional[Dict[str, Any]] = None):
        """
        Initialize with logger and operation.
        
        Args:
            logger: Logging service
            operation: Operation name
            metadata: Additional metadata
            context: Additional context
        """
        self.logger = logger
        self.operation = operation
        self.metadata = metadata
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """
        Start timing operation.
        
        Returns:
            Self
        """
        self.start_time = time.time()
        self.logger.log_debug(
            f"Starting operation: {self.operation}",
            self.metadata,
            self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        End timing operation and log performance.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            # Operation failed
            self.logger.log_exception(
                exc_val,
                f"Operation failed: {self.operation}",
                self.metadata,
                self.context
            )
        else:
            # Operation succeeded
            self.logger.log_performance(
                self.operation,
                duration,
                self.metadata,
                self.context
            )
```

## Features to Implement

1. **Structured Logging**
   - JSON-formatted log entries
   - Consistent metadata structure
   - Correlation IDs for request tracking
   - Context-aware logging

2. **Multiple Output Destinations**
   - Console logging with color support
   - File logging with rotation
   - JSON logging for machine processing
   - External service integration (e.g., ELK, Datadog)

3. **Performance Monitoring**
   - Operation timing
   - Resource usage tracking
   - Throughput metrics
   - Latency measurements

4. **Error Tracking**
   - Exception logging with stack traces
   - Error categorization
   - Error frequency analysis
   - Alert triggering for critical errors

5. **Log Management**
   - Log rotation and archiving
   - Log level filtering
   - Log search and analysis
   - Log retention policies

## Testing Strategy

### Unit Tests

1. **Handler Tests**
   - Test each handler independently
   - Verify correct formatting of log entries
   - Test level filtering
   - Verify file rotation

2. **Service Tests**
   - Test logging at different levels
   - Verify context propagation
   - Test performance logging
   - Verify exception logging

3. **Context Manager Tests**
   - Test timed operation context manager
   - Verify correct timing calculation
   - Test exception handling
   - Verify metadata propagation

### Integration Tests

1. **Component Integration Tests**
   - Test logging service with other components
   - Verify log entries contain expected information
   - Test correlation ID propagation
   - Verify performance metrics

2. **System Tests**
   - Test logging in complete system
   - Verify log files are created and rotated
   - Test log search and analysis
   - Verify error tracking

### Performance Tests

1. **Throughput Tests**
   - Measure logging throughput
   - Test with high log volume
   - Verify handler performance
   - Measure impact on system performance

2. **Resource Usage Tests**
   - Measure memory usage
   - Test file size management
   - Verify CPU usage
   - Test with limited resources

## Example Usage

```python
from typing import Dict, Any
import os

def main():
    # Create log directory
    os.makedirs("logs", exist_ok=True)
    
    # Initialize handlers
    console_handler = ConsoleLogHandler(min_level="info")
    file_handler = FileLogHandler("logs/extraction.log", min_level="debug")
    json_handler = JsonLogHandler("logs/extraction.json", min_level="info")
    
    # Initialize logging service
    logger = LoggingService(
        handlers=[console_handler, file_handler, json_handler],
        context={"application": "extraction-service"}
    )
    
    # Log messages at different levels
    logger.log_debug("This is a debug message")
    logger.log_info("This is an info message", {"user": "john"})
    logger.log_warning("This is a warning message", {"source": "config"})
    logger.log_error("This is an error message", {"code": 500})
    
    # Log with additional context
    logger.log_info(
        "Processing document",
        {"document_id": "doc123", "size": 1024},
        {"request_id": "req456"}
    )
    
    # Log exception
    try:
        result = 1 / 0
    except Exception as e:
        logger.log_exception(e, "Division by zero")
    
    # Log performance
    logger.log_performance("document_processing", 1.234, {"document_id": "doc123"})
    
    # Use timed operation context manager
    with logger.timed_operation("document_chunking", {"document_id": "doc123"}):
        # Simulate work
        import time
        time.sleep(0.5)
    
    # Close handlers
    logger.close()

# Run the function
main()
```

## Example Log Output

### Console Output
```
2023-05-15 10:30:45.123 INFO [abc123] This is an info message {"user": "john", "log_id": "def456"}
2023-05-15 10:30:45.124 WARNING [abc123] This is a warning message {"source": "config", "log_id": "ghi789"}
2023-05-15 10:30:45.125 ERROR [abc123] This is an error message {"code": 500, "log_id": "jkl012"}
2023-05-15 10:30:45.126 INFO [abc123] Processing document {"document_id": "doc123", "size": 1024, "log_id": "mno345"}
2023-05-15 10:30:45.127 ERROR [abc123] Division by zero {"exception": {"type": "ZeroDivisionError", "message": "division by zero", "traceback": "..."}, "log_id": "pqr678"}
2023-05-15 10:30:45.128 INFO [abc123] Performance: document_processing took 1.234000 seconds {"performance": {"operation": "document_processing", "duration": 1.234}, "document_id": "doc123", "log_id": "stu901"}
2023-05-15 10:30:45.129 DEBUG [abc123] Starting operation: document_chunking {"document_id": "doc123", "log_id": "vwx234"}
2023-05-15 10:30:45.630 INFO [abc123] Performance: document_chunking took 0.500000 seconds {"performance": {"operation": "document_chunking", "duration": 0.5}, "document_id": "doc123", "log_id": "yz0123"}
```

### JSON Output
```json
{"timestamp": "2023-05-15T10:30:45.123456", "level": "INFO", "message": "This is an info message", "context": {"application": "extraction-service", "correlation_id": "abc123"}, "metadata": {"user": "john", "log_id": "def456"}}
{"timestamp": "2023-05-15T10:30:45.124456", "level": "WARNING", "message": "This is a warning message", "context": {"application": "extraction-service", "correlation_id": "abc123"}, "metadata": {"source": "config", "log_id": "ghi789"}}
{"timestamp": "2023-05-15T10:30:45.125456", "level": "ERROR", "message": "This is an error message", "context": {"application": "extraction-service", "correlation_id": "abc123"}, "metadata": {"code": 500, "log_id": "jkl012"}}
{"timestamp": "2023-05-15T10:30:45.126456", "level": "INFO", "message": "Processing document", "context": {"application": "extraction-service", "correlation_id": "abc123", "request_id": "req456"}, "metadata": {"document_id": "doc123", "size": 1024, "log_id": "mno345"}}
{"timestamp": "2023-05-15T10:30:45.127456", "level": "ERROR", "message": "Division by zero", "context": {"application": "extraction-service", "correlation_id": "abc123"}, "metadata": {"exception": {"type": "ZeroDivisionError", "message": "division by zero", "traceback": "..."}, "log_id": "pqr678"}}
{"timestamp": "2023-05-15T10:30:45.128456", "level": "INFO", "message": "Performance: document_processing took 1.234000 seconds", "context": {"application": "extraction-service", "correlation_id": "abc123"}, "metadata": {"performance": {"operation": "document_processing", "duration": 1.234}, "document_id": "doc123", "log_id": "stu901"}}
{"timestamp": "2023-05-15T10:30:45.129456", "level": "DEBUG", "message": "Starting operation: document_chunking", "context": {"application": "extraction-service", "correlation_id": "abc123"}, "metadata": {"document_id": "doc123", "log_id": "vwx234"}}
{"timestamp": "2023-05
