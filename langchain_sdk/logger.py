"""
Rich Console Logger for Extraction Pipeline

This module provides a rich console logger for the extraction pipeline.
"""

import time
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich import box

class RichLogger:
    """Rich console logger for extraction pipeline."""
    
    def __init__(self, verbose: bool = True, log_to_file: Optional[str] = None):
        """
        Initialize rich console logger.
        
        Args:
            verbose: Whether to log verbose output
            log_to_file: Path to log file (optional)
        """
        self.verbose = verbose
        self.console = Console(record=log_to_file is not None)
        self.log_to_file = log_to_file
        self.start_time = time.time()
        self.step_times = {}
        
    def start_pipeline(self, config: Dict[str, Any]) -> None:
        """
        Log pipeline start.
        
        Args:
            config: Pipeline configuration
        """
        self.start_time = time.time()
        
        if not self.verbose:
            return
            
        # Create table for configuration
        table = Table(title="Extraction Pipeline Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        # Add LLM configuration
        llm_name = config.get("llm_name", "Unknown")
        llm_model = config.get("llm_model", "Unknown")
        table.add_row("LLM Provider", llm_name)
        table.add_row("LLM Model", llm_model)
        
        # Add embedder configuration
        embedder_name = config.get("embedder_name", "Unknown")
        embedder_model = config.get("embedder_model", "Unknown")
        table.add_row("Embedder Provider", embedder_name)
        table.add_row("Embedder Model", embedder_model)
        
        # Add other configuration
        table.add_row("Max Concurrency", str(config.get("max_concurrency", "Unknown")))
        table.add_row("Chunk Size", str(config.get("chunk_size", "Unknown")))
        table.add_row("Chunk Overlap", str(config.get("chunk_overlap", "Unknown")))
        
        # Print table
        self.console.print(Panel(table, title="Starting Extraction Pipeline", subtitle="Initializing components..."))
        
    def log_step(self, step_name: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log pipeline step.
        
        Args:
            step_name: Step name
            message: Step message
            data: Step data (optional)
        """
        if not self.verbose:
            return
            
        # Record step time
        self.step_times[step_name] = time.time()
        
        # Create panel for step
        self.console.print(f"[bold cyan]STEP:[/bold cyan] [bold green]{step_name}[/bold green] - {message}")
        
        # Print data if provided
        if data:
            data_table = Table(box=box.SIMPLE)
            data_table.add_column("Key", style="cyan")
            data_table.add_column("Value", style="green")
            
            for key, value in data.items():
                data_table.add_row(key, str(value))
                
            self.console.print(data_table)
            
    def log_document_loading(self, document_path: str, document_count: int, page_count: int) -> None:
        """
        Log document loading.
        
        Args:
            document_path: Document path
            document_count: Number of documents
            page_count: Number of pages
        """
        if not self.verbose:
            return
            
        self.console.print(Panel(
            f"Loaded [bold green]{document_count}[/bold green] documents with [bold green]{page_count}[/bold green] pages from [bold cyan]{document_path}[/bold cyan]",
            title="Document Loading",
            border_style="green"
        ))
        
    def log_chunking(self, chunk_count: int, chunk_size: int, chunk_overlap: int) -> None:
        """
        Log document chunking.
        
        Args:
            chunk_count: Number of chunks
            chunk_size: Chunk size
            chunk_overlap: Chunk overlap
        """
        if not self.verbose:
            return
            
        self.console.print(Panel(
            f"Split documents into [bold green]{chunk_count}[/bold green] chunks with size [bold cyan]{chunk_size}[/bold cyan] and overlap [bold cyan]{chunk_overlap}[/bold cyan]",
            title="Document Chunking",
            border_style="green"
        ))
        
    def log_llm_request(self, chunk_index: int, chunk_size: int, prompt_tokens: int) -> None:
        """
        Log LLM request.
        
        Args:
            chunk_index: Chunk index
            chunk_size: Chunk size
            prompt_tokens: Prompt tokens
        """
        if not self.verbose:
            return
            
        self.console.print(f"[bold cyan]LLM Request:[/bold cyan] Chunk {chunk_index+1} ({chunk_size} chars, ~{prompt_tokens} tokens)")
        
    def log_llm_response(self, chunk_index: int, completion_tokens: int, success: bool, error: Optional[str] = None) -> None:
        """
        Log LLM response.
        
        Args:
            chunk_index: Chunk index
            completion_tokens: Completion tokens
            success: Whether the request was successful
            error: Error message (if any)
        """
        if not self.verbose:
            return
            
        if success:
            self.console.print(f"[bold green]LLM Response:[/bold green] Chunk {chunk_index+1} (~{completion_tokens} tokens)")
        else:
            self.console.print(f"[bold red]LLM Error:[/bold red] Chunk {chunk_index+1} - {error}")
            
    def create_progress(self, total: int, description: str) -> Progress:
        """
        Create progress bar.
        
        Args:
            total: Total number of steps
            description: Progress description
            
        Returns:
            Progress bar
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold green]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=self.console
        )
        
    def log_extraction_results(self, results: Dict[str, Any], format_type: str) -> None:
        """
        Log extraction results.
        
        Args:
            results: Extraction results
            format_type: Format type (json, text, xml)
        """
        if not self.verbose:
            return
            
        if format_type == "json":
            import json
            syntax = Syntax(json.dumps(results, indent=2), "json", theme="monokai", line_numbers=True)
            self.console.print(Panel(syntax, title=f"JSON Output", border_style="green"))
        elif format_type == "text":
            syntax = Syntax(results, "text", theme="monokai")
            self.console.print(Panel(syntax, title=f"Text Output", border_style="green"))
        elif format_type == "xml":
            syntax = Syntax(results[:500] + "..." if len(results) > 500 else results, "xml", theme="monokai")
            self.console.print(Panel(syntax, title=f"XML Output (first 500 chars)", border_style="green"))
            
    def log_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Log metadata.
        
        Args:
            metadata: Metadata
        """
        if not self.verbose:
            return
            
        # Create table for metadata
        table = Table(title="Extraction Metadata", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Add metadata
        for key, value in metadata.items():
            table.add_row(key.replace("_", " ").title(), str(value))
            
        # Add total processing time
        total_time = time.time() - self.start_time
        table.add_row("Total Processing Time", f"{total_time:.2f} seconds")
        
        # Print table
        self.console.print(Panel(table, title="Extraction Complete", border_style="green"))
        
    def log_error(self, error_message: str, error_details: Optional[str] = None) -> None:
        """
        Log error.
        
        Args:
            error_message: Error message
            error_details: Error details (optional)
        """
        self.console.print(Panel(
            f"[bold red]{error_message}[/bold red]\n\n{error_details if error_details else ''}",
            title="Error",
            border_style="red"
        ))
        
    def save_log(self) -> None:
        """Save log to file."""
        if self.log_to_file:
            self.console.save_html(self.log_to_file)
            self.console.print(f"Log saved to [bold cyan]{self.log_to_file}[/bold cyan]")
