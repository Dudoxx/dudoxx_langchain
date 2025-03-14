# Rich Logger

The `RichLogger` is a powerful logging component in the Dudoxx Extraction system that provides detailed, colorful, and well-formatted console output for better visibility and debugging.

## Overview

Effective logging is crucial for understanding the behavior of complex systems like the Dudoxx Extraction pipeline. The `RichLogger` leverages the [Rich](https://github.com/Textualize/rich) library to provide beautiful console output with syntax highlighting, tables, progress bars, and more.

This component logs various aspects of the extraction process, including document loading, chunking, LLM requests and responses, extraction results, and metadata. The logs are formatted in a way that makes it easy to understand what's happening at each step of the process.

## Key Features

1. **Colorful Console Output**: Uses colors and formatting for better readability
2. **Step-by-Step Logging**: Logs each step of the extraction process
3. **Syntax Highlighting**: Highlights JSON, XML, and other structured data
4. **Tabular Data**: Displays tabular data in a readable format
5. **Error Highlighting**: Highlights errors for easier debugging
6. **Verbose Mode**: Supports a verbose mode for more detailed logging
7. **Metadata Tracking**: Logs metadata about the extraction process

## Implementation

The `RichLogger` class is implemented in `langchain_sdk/logger.py`. Here's a simplified version of the class:

```python
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich import box
import time

class RichLogger:
    def __init__(self, verbose=False):
        self.console = Console()
        self.verbose = verbose
        self.start_time = time.time()
        self.steps = []
    
    def log_step(self, step_name, message, data=None):
        """Log a step in the extraction process."""
        if not self.verbose and step_name not in ["Error", "Warning"]:
            return
            
        self.steps.append(step_name)
        
        if data:
            # Create a table for the data
            table = Table(box=box.SIMPLE)
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in data.items():
                table.add_row(str(key), str(value))
            
            self.console.print(f"STEP: {step_name} - {message}")
            self.console.print(table)
        else:
            self.console.print(f"STEP: {step_name} - {message}")
    
    def log_error(self, message, details=None):
        """Log an error."""
        self.console.print(f"ERROR: {message}", style="bold red")
        if details:
            self.console.print(Panel(details, title="Error Details", border_style="red"))
    
    def start_pipeline(self, config):
        """Log the start of the extraction pipeline."""
        self.start_time = time.time()
        
        # Create a table for the configuration
        table = Table(title="Extraction Pipeline Configuration", box=box.SIMPLE)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in config.items():
            table.add_row(str(key), str(value))
        
        # Create a panel for the table
        panel = Panel(
            table,
            title="Starting Extraction Pipeline",
            border_style="cyan",
            expand=False
        )
        
        self.console.print(panel)
        self.console.print("Initializing components...")
    
    def log_document_loading(self, document_path, document_count, page_count):
        """Log document loading."""
        panel = Panel(
            f"Loaded {document_count} documents with {page_count} pages from {document_path}",
            title="Document Loading",
            border_style="green"
        )
        self.console.print(panel)
    
    def log_chunking(self, chunk_count, chunk_size, chunk_overlap):
        """Log document chunking."""
        panel = Panel(
            f"Split documents into {chunk_count} chunks with size {chunk_size} and overlap {chunk_overlap}",
            title="Document Chunking",
            border_style="green"
        )
        self.console.print(panel)
    
    def log_llm_request(self, chunk_index, chunk_size, token_count):
        """Log an LLM request."""
        if not self.verbose:
            return
            
        self.console.print(f"LLM Request: Chunk {chunk_index + 1} ({chunk_size} chars ~{token_count} tokens)")
    
    def log_llm_response(self, chunk_index, token_count, success, error_message=None):
        """Log an LLM response."""
        if not self.verbose:
            return
            
        if success:
            self.console.print(f"LLM Response: Chunk {chunk_index + 1} (~{token_count} tokens)")
        else:
            self.console.print(f"LLM Response: Chunk {chunk_index + 1} (Failed: {error_message})", style="bold red")
    
    def log_extraction_results(self, result, format_type):
        """Log extraction results."""
        if not self.verbose:
            return
            
        if format_type == "json":
            # Format as JSON
            if isinstance(result, dict):
                json_str = json.dumps(result, indent=2)
                syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
                panel = Panel(syntax, title="JSON Output", border_style="green")
                self.console.print(panel)
            else:
                self.console.print(result)
        elif format_type == "text":
            # Format as text
            panel = Panel(result, title="Text Output", border_style="green")
            self.console.print(panel)
        elif format_type == "xml":
            # Format as XML
            if len(result) > 500:
                syntax = Syntax(result[:500] + "...", "xml", theme="monokai")
                panel = Panel(syntax, title="XML Output (first 500 chars)", border_style="green")
            else:
                syntax = Syntax(result, "xml", theme="monokai")
                panel = Panel(syntax, title="XML Output", border_style="green")
            self.console.print(panel)
    
    def log_metadata(self, metadata):
        """Log metadata about the extraction process."""
        # Create a table for the metadata
        table = Table(title="Extraction Metadata", box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in metadata.items():
            table.add_row(str(key), str(value))
        
        # Add total processing time
        processing_time = time.time() - self.start_time
        table.add_row("Total Processing Time", f"{processing_time:.2f} seconds")
        
        # Create a panel for the table
        panel = Panel(
            table,
            title="Extraction Complete",
            border_style="green",
            expand=False
        )
        
        self.console.print(panel)
```

## Logging Process

The `RichLogger` provides methods for logging various aspects of the extraction process:

1. **Pipeline Initialization**: Logs the configuration of the extraction pipeline.
2. **Document Loading**: Logs information about the loaded documents.
3. **Document Chunking**: Logs information about the document chunks.
4. **LLM Requests**: Logs information about LLM requests, including chunk index and token count.
5. **LLM Responses**: Logs information about LLM responses, including success status and token count.
6. **Extraction Results**: Logs the extraction results in various formats (JSON, text, XML).
7. **Metadata**: Logs metadata about the extraction process, including processing time and token usage.

## Usage Example

```python
# Initialize logger
logger = RichLogger(verbose=True)

# Log pipeline initialization
logger.start_pipeline({
    "llm_name": "ChatOpenAI",
    "llm_model": "gpt-4",
    "embedder_name": "OpenAIEmbeddings",
    "embedder_model": "text-embedding-ada-002",
    "max_concurrency": 20,
    "chunk_size": 16000,
    "chunk_overlap": 200
})

# Log document loading
logger.log_document_loading("examples/medical_record.txt", 1, 10)

# Log document chunking
logger.log_chunking(5, 16000, 200)

# Log LLM request
logger.log_llm_request(0, 16000, 4000)

# Log LLM response
logger.log_llm_response(0, 1000, True)

# Log extraction results
logger.log_extraction_results({"patient_name": "John Smith"}, "json")

# Log metadata
logger.log_metadata({
    "processing_time": 5.2,
    "chunk_count": 5,
    "field_count": 10,
    "prompt_tokens": 4000,
    "completion_tokens": 1000,
    "total_tokens": 5000
})
```

## Integration with Extraction Pipeline

The `RichLogger` is integrated into the extraction pipeline and is used to log each step of the process:

```python
# In ExtractionPipeline.__init__
self.logger = logger

# In ExtractionPipeline.process_document
if self.logger:
    self.logger.log_step("Document Loading", f"Loading document from {document_path}")
    
# After loading document
if self.logger:
    self.logger.log_document_loading(document_path, len(documents), page_count)

# Before processing chunks
if self.logger:
    self.logger.log_step("Chunk Processing", f"Processing {len(chunks)} chunks with concurrency {self.max_concurrency}")

# Before LLM request
if self.logger:
    self.logger.log_llm_request(chunk_index, len(chunk.page_content), prompt_tokens)

# After LLM response
if self.logger:
    self.logger.log_llm_response(chunk_index, completion_tokens, True)

# After formatting output
if self.logger:
    self.logger.log_extraction_results(output["json_output"], "json")

# After processing document
if self.logger:
    self.logger.log_metadata(metadata)
```

## Benefits

1. **Visibility**: Provides clear visibility into the extraction process.
2. **Debugging**: Makes it easier to debug issues by highlighting errors and providing detailed information.
3. **Performance Monitoring**: Tracks processing time and token usage for performance monitoring.
4. **User Experience**: Enhances the user experience with colorful and well-formatted output.
5. **Customizability**: Can be customized to log additional information as needed.

## Customization

The `RichLogger` can be customized in several ways:

1. **Verbose Mode**: Enable or disable verbose mode to control the amount of logging.
2. **Log Formats**: Customize the format of logs for different types of information.
3. **Color Schemes**: Adjust the color scheme to match your preferences.
4. **Additional Logging**: Add methods for logging additional aspects of the extraction process.
5. **Output Redirection**: Redirect logs to a file or other output stream.

## Example Output

Here's an example of the console output produced by the `RichLogger`:

```
╭──────────────────────────────────────────────────────────────────── Starting Extraction Pipeline ─────────────────────────────────────────────────────────────────────╮
│    Extraction Pipeline Configuration                                                                                                                                  │
│ ╭───────────────────┬──────────────────╮                                                                                                                              │
│ │ Setting           │ Value            │                                                                                                                              │
│ ├───────────────────┼──────────────────┤                                                                                                                              │
│ │ LLM Provider      │ ChatOpenAI       │                                                                                                                              │
│ │ LLM Model         │ gpt-4            │                                                                                                                              │
│ │ Embedder Provider │ OpenAIEmbeddings │                                                                                                                              │
│ │ Embedder Model    │ text-embedding-ada-002 │                                                                                                                        │
│ │ Max Concurrency   │ 20               │                                                                                                                              │
│ │ Chunk Size        │ 16000            │                                                                                                                              │
│ │ Chunk Overlap     │ 200              │                                                                                                                              │
│ ╰───────────────────┴──────────────────╯                                                                                                                              │
╰───────────────────────────────────────────────────────────────────── Initializing components... ──────────────────────────────────────────────────────────────────────╯

STEP: Document Loading - Loading document from examples/medical_record.txt

╭────────────────────────────────────────────────────────────────────────── Document Loading ───────────────────────────────────────────────────────────────────────────╮
│ Loaded 1 documents with 10 pages from examples/medical_record.txt                                                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

STEP: Document Chunking - Splitting document into chunks

╭────────────────────────────────────────────────────────────────────────── Document Chunking ──────────────────────────────────────────────────────────────────────────╮
│ Split documents into 1 chunks with size 16000 and overlap 200                                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

STEP: Chunk Processing - Processing 1 chunks with concurrency 20

LLM Request: Chunk 1 (2050 chars ~630 tokens)
LLM Response: Chunk 1 (~266 tokens)

STEP: Temporal Normalization - Normalizing temporal data
STEP: Result Merging - Merging and deduplicating results
STEP: Result Merging - Merging results from 1 chunks
STEP: Result Merging - Merged 5 fields
STEP: Output Formatting - Formatting output in ['json', 'text', 'xml']
STEP: Output Formatting - Formatting output as JSON

╭───────────────────────────────────────────────────────────────────────────── JSON Output ─────────────────────────────────────────────────────────────────────────────╮
│    1 {                                                                                                                                                                │
│    2   "patient_name": "John Smith",                                                                                                                                 │
│    3   "date_of_birth": "05/15/1980",                                                                                                                                │
│    4   "diagnoses": [                                                                                                                                                 │
│    5     "Type 2 Diabetes",                                                                                                                                          │
│    6     "Hypertension",                                                                                                                                             │
│    7     "Upper respiratory infection"                                                                                                                                │
│    8   ],                                                                                                                                                            │
│    9   "medications": [                                                                                                                                               │
│   10     "Metformin 500mg twice daily (for diabetes)",                                                                                                              │
│   11     "Lisinopril 10mg once daily (for hypertension)",                                                                                                           │
│   12     "Aspirin 81mg once daily (preventative)"                                                                                                                    │
│   13   ],                                                                                                                                                            │
│   14   "visits": [                                                                                                                                                    │
│   15     {                                                                                                                                                            │
│   16       "date": "03/10/2023",                                                                                                                                     │
│   17       "description": "Upper respiratory infection, likely viral"                                                                                                │
│   18     },                                                                                                                                                          │
│   19     {                                                                                                                                                            │
│   20       "date": "07/22/2023",                                                                                                                                     │
│   21       "description": "Type 2 Diabetes - well controlled"                                                                                                        │
│   22     },                                                                                                                                                          │
│   23     {                                                                                                                                                            │
│   24       "date": "11/15/2023",                                                                                                                                     │
│   25       "description": "Overall good health, mild hyperlipidemia"                                                                                                │
│   26     }                                                                                                                                                            │
│   27   ]                                                                                                                                                             │
│   28 }                                                                                                                                                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

STEP: Output Formatting - Formatting output as text

╭───────────────────────────────────────────────────────────────────────────── Text Output ─────────────────────────────────────────────────────────────────────────────╮
│ patient_name: John Smith                                                                                                                                              │
│ date_of_birth: 05/15/1980                                                                                                                                             │
│ diagnoses: Type 2 Diabetes                                                                                                                                            │
│ diagnoses: Hypertension                                                                                                                                               │
│ diagnoses: Upper respiratory infection                                                                                                                                │
│ medications: Metformin 500mg twice daily (for diabetes)                                                                                                              │
│ medications: Lisinopril 10mg once daily (for hypertension)                                                                                                           │
│ medications: Aspirin 81mg once daily (preventative)                                                                                                                  │
│ visits: date: 03/10/2023, description: Upper respiratory infection, likely viral                                                                                     │
│ visits: date: 07/22/2023, description: Type 2 Diabetes - well controlled                                                                                             │
│ visits: date: 11/15/2023, description: Overall good health, mild hyperlipidemia                                                                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

STEP: Output Formatting - Formatting output as XML

╭──────────────────────────────────────────────────────────────────── XML Output (first 500 chars) ─────────────────────────────────────────────────────────────────────╮
│ <?xml version="1.0" ?>                                                                                                                                                │
│ <Document>                                                                                                                                                            │
│   <Fields>                                                                                                                                                            │
│     <patient_name>John Smith</patient_name>                                                                                                                           │
│     <date_of_birth>05/15/1980</date_of_birth>                                                                                                                         │
│     <diagnoses>                                                                                                                                                       │
│       <Item>Type 2 Diabetes</Item>                                                                                                                                    │
│       <Item>Hypertension</Item>                                                                                                                                       │
│       <Item>Upper respiratory infection</Item>                                                                                                                        │
│     </diagnoses>                                                                                                                                                      │
│     <medications>                                                                                                                                                     │
│       <Item>Metformin 500mg twice daily (for diabetes)</Item>                                                                                                        │
│       <Item>Lisinopril 10mg once daily (for hypertension)</Item>                                                                                                     │
│       <Item>Aspirin 81mg once daily (preventative)</Item>                                                                                                            │
│     </medica...                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭───────────────────────────────────────────────────────────────────────── Extraction Complete ─────────────────────────────────────────────────────────────────────────╮
│              Extraction Metadata                                                                                                                                      │
│ ╭───────────────────────┬────────────────────╮                                                                                                                        │
│ │ Metric                │ Value              │                                                                                                                        │
│ ├───────────────────────┼────────────────────┤                                                                                                                        │
│ │ Processing Time       │ 7.3423240184783936 │                                                                                                                        │
│ │ Chunk Count           │ 1                  │                                                                                                                        │
│ │ Field Count           │ 5                  │                                                                                                                        │
│ │ Prompt Tokens         │ 512                │                                                                                                                        │
│ │ Completion Tokens     │ 234                │                                                                                                                        │
│ │ Total Tokens          │ 746                │                                                                                                                        │
│ │ Total Processing Time │ 7.34 seconds       │                                                                                                                        │
│ ╰───────────────────────┴────────────────────╯                                                                                                                        │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
