"""
Progress Tracker for Dudoxx Extraction.

This module provides a progress tracking system with callbacks for the extraction pipelines.
"""

from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from rich.console import Console
import os

# Initialize console for logging
console = Console()

class ExtractionPhase(Enum):
    """Extraction phases for progress tracking."""
    INITIALIZATION = "initialization"
    DOCUMENT_LOADING = "document_loading"
    DOCUMENT_CHUNKING = "document_chunking"
    DOMAIN_IDENTIFICATION = "domain_identification"
    FIELD_EXTRACTION = "field_extraction"
    TEMPORAL_NORMALIZATION = "temporal_normalization"
    RESULT_MERGING = "result_merging"
    DEDUPLICATION = "deduplication"
    OUTPUT_FORMATTING = "output_formatting"
    COMPLETION = "completion"
    ERROR = "error"

class ProgressTracker:
    """
    Progress tracker for extraction pipelines.
    
    This class tracks progress of extraction pipelines and sends updates
    via callbacks.
    """
    
    def __init__(
        self, 
        request_id: Optional[str] = None,
        total_steps: int = 100,
        callback: Optional[Callable[[str, str, str, Optional[int]], None]] = None
    ):
        """
        Initialize progress tracker.
        
        Args:
            request_id: Request ID for progress updates
            total_steps: Total number of steps in the extraction process
            callback: Callback function for progress updates
        """
        self.request_id = request_id
        self.total_steps = total_steps
        self.current_step = 0
        self.callback = callback
        self.phase = ExtractionPhase.INITIALIZATION
        
        # Phase weights for percentage calculation
        self.phase_weights = {
            ExtractionPhase.INITIALIZATION: 5,
            ExtractionPhase.DOCUMENT_LOADING: 5,
            ExtractionPhase.DOCUMENT_CHUNKING: 5,
            ExtractionPhase.DOMAIN_IDENTIFICATION: 10,
            ExtractionPhase.FIELD_EXTRACTION: 50,  # Largest portion of work
            ExtractionPhase.TEMPORAL_NORMALIZATION: 5,
            ExtractionPhase.RESULT_MERGING: 10,
            ExtractionPhase.DEDUPLICATION: 5,
            ExtractionPhase.OUTPUT_FORMATTING: 5,
            ExtractionPhase.COMPLETION: 0,  # Final state
            ExtractionPhase.ERROR: 0  # Error state
        }
        
        # Phase base percentages (cumulative)
        self.phase_base_percentages = {}
        cumulative = 0
        for phase, weight in self.phase_weights.items():
            self.phase_base_percentages[phase] = cumulative
            cumulative += weight
        
        # Track sub-tasks for complex phases
        self.subtasks = {
            ExtractionPhase.FIELD_EXTRACTION: {
                "total": 0,
                "completed": 0,
                "current_message": ""
            }
        }
        
        # Send initial progress update
        self.update_progress(
            ExtractionPhase.INITIALIZATION,
            "Starting extraction process...",
            0
        )
    
    def update_progress(
        self, 
        phase: ExtractionPhase, 
        message: str, 
        phase_progress: Optional[int] = None
    ):
        """
        Update progress and send callback.
        
        Args:
            phase: Current extraction phase
            message: Progress message
            phase_progress: Progress within the current phase (0-100)
        """
        self.phase = phase
        
        # Calculate overall percentage
        base_percentage = self.phase_base_percentages[phase]
        phase_weight = self.phase_weights[phase]
        
        if phase_progress is not None:
            # Calculate percentage within the phase
            percentage = base_percentage + (phase_weight * phase_progress / 100)
        else:
            # Use the base percentage for the phase
            percentage = base_percentage
        
        # Round to nearest integer
        percentage = round(percentage)
        
        # Ensure percentage is between 0 and 100
        percentage = max(0, min(100, percentage))
        
        # Log progress
        console.print(f"[blue]Progress update:[/] {phase.value} - {message} ({percentage}%)")
        
        # Send callback if available
        if self.callback and self.request_id:
            status = "completed" if phase == ExtractionPhase.COMPLETION else \
                     "error" if phase == ExtractionPhase.ERROR else \
                     "processing"
            
            self.callback(self.request_id, status, message, percentage)
    
    def set_field_extraction_tasks(self, total_tasks: int):
        """
        Set the total number of field extraction tasks.
        
        Args:
            total_tasks: Total number of tasks
        """
        self.subtasks[ExtractionPhase.FIELD_EXTRACTION]["total"] = total_tasks
        self.subtasks[ExtractionPhase.FIELD_EXTRACTION]["completed"] = 0
    
    def update_field_extraction_progress(self, message: str, completed_tasks: Optional[int] = None):
        """
        Update progress for field extraction phase.
        
        Args:
            message: Progress message
            completed_tasks: Number of completed tasks (if None, increment by 1)
        """
        subtask = self.subtasks[ExtractionPhase.FIELD_EXTRACTION]
        
        if completed_tasks is not None:
            subtask["completed"] = completed_tasks
        else:
            subtask["completed"] += 1
        
        subtask["current_message"] = message
        
        # Calculate progress within the field extraction phase
        if subtask["total"] > 0:
            phase_progress = (subtask["completed"] / subtask["total"]) * 100
        else:
            phase_progress = 50  # Default to 50% if no tasks
        
        # Update overall progress
        self.update_progress(
            ExtractionPhase.FIELD_EXTRACTION,
            message,
            phase_progress
        )
    
    def start_document_loading(self, document_type: str, document_info: str = ""):
        """
        Start document loading phase.
        
        Args:
            document_type: Type of document (e.g., "PDF", "DOCX")
            document_info: Additional document information
        """
        message = f"Loading {document_type} document{' ' + document_info if document_info else ''}..."
        self.update_progress(ExtractionPhase.DOCUMENT_LOADING, message, 0)
    
    def complete_document_loading(self, page_count: int):
        """
        Complete document loading phase.
        
        Args:
            page_count: Number of pages loaded
        """
        message = f"Document loaded successfully ({page_count} pages)"
        self.update_progress(ExtractionPhase.DOCUMENT_LOADING, message, 100)
    
    def start_document_chunking(self, page_count: int):
        """
        Start document chunking phase.
        
        Args:
            page_count: Number of pages to chunk
        """
        message = f"Splitting document into chunks ({page_count} pages)..."
        self.update_progress(ExtractionPhase.DOCUMENT_CHUNKING, message, 0)
    
    def complete_document_chunking(self, chunk_count: int):
        """
        Complete document chunking phase.
        
        Args:
            chunk_count: Number of chunks created
        """
        message = f"Document split into {chunk_count} chunks"
        self.update_progress(ExtractionPhase.DOCUMENT_CHUNKING, message, 100)
    
    def start_domain_identification(self, query: str):
        """
        Start domain identification phase.
        
        Args:
            query: Query for domain identification
        """
        message = f"Identifying domains for query: {query[:50]}..."
        self.update_progress(ExtractionPhase.DOMAIN_IDENTIFICATION, message, 0)
    
    def complete_domain_identification(self, domain: str, fields: List[str]):
        """
        Complete domain identification phase.
        
        Args:
            domain: Identified domain
            fields: Identified fields
        """
        message = f"Identified domain: {domain} with {len(fields)} fields"
        self.update_progress(ExtractionPhase.DOMAIN_IDENTIFICATION, message, 100)
    
    def start_field_extraction(self, chunk_count: int, field_count: int):
        """
        Start field extraction phase.
        
        Args:
            chunk_count: Number of chunks to process
            field_count: Number of fields to extract
        """
        total_tasks = chunk_count * field_count
        self.set_field_extraction_tasks(total_tasks)
        
        message = f"Extracting {field_count} fields from {chunk_count} chunks..."
        self.update_progress(ExtractionPhase.FIELD_EXTRACTION, message, 0)
    
    def update_chunk_progress(self, chunk_index: int, chunk_count: int, field_name: str = ""):
        """
        Update progress for chunk processing.
        
        Args:
            chunk_index: Current chunk index
            chunk_count: Total number of chunks
            field_name: Current field name
        """
        field_info = f" (field: {field_name})" if field_name else ""
        message = f"Processing chunk {chunk_index + 1}/{chunk_count}{field_info}..."
        self.update_field_extraction_progress(message)
    
    def start_temporal_normalization(self):
        """Start temporal normalization phase."""
        message = "Normalizing temporal data..."
        self.update_progress(ExtractionPhase.TEMPORAL_NORMALIZATION, message, 0)
    
    def complete_temporal_normalization(self, field_count: int):
        """
        Complete temporal normalization phase.
        
        Args:
            field_count: Number of fields normalized
        """
        message = f"Temporal data normalized for {field_count} fields"
        self.update_progress(ExtractionPhase.TEMPORAL_NORMALIZATION, message, 100)
    
    def start_result_merging(self, chunk_count: int):
        """
        Start result merging phase.
        
        Args:
            chunk_count: Number of chunks to merge
        """
        message = f"Merging results from {chunk_count} chunks..."
        self.update_progress(ExtractionPhase.RESULT_MERGING, message, 0)
    
    def update_result_merging(self, merged_count: int, total_count: int):
        """
        Update result merging progress.
        
        Args:
            merged_count: Number of chunks merged
            total_count: Total number of chunks
        """
        percentage = (merged_count / total_count) * 100 if total_count > 0 else 50
        message = f"Merged {merged_count}/{total_count} chunks..."
        self.update_progress(ExtractionPhase.RESULT_MERGING, message, percentage)
    
    def complete_result_merging(self, field_count: int):
        """
        Complete result merging phase.
        
        Args:
            field_count: Number of fields in merged result
        """
        message = f"Results merged successfully ({field_count} fields)"
        self.update_progress(ExtractionPhase.RESULT_MERGING, message, 100)
    
    def start_deduplication(self):
        """Start deduplication phase."""
        message = "Deduplicating results..."
        self.update_progress(ExtractionPhase.DEDUPLICATION, message, 0)
    
    def complete_deduplication(self, duplicate_count: int):
        """
        Complete deduplication phase.
        
        Args:
            duplicate_count: Number of duplicates removed
        """
        message = f"Deduplication completed ({duplicate_count} duplicates removed)"
        self.update_progress(ExtractionPhase.DEDUPLICATION, message, 100)
    
    def start_output_formatting(self, formats: List[str]):
        """
        Start output formatting phase.
        
        Args:
            formats: Output formats
        """
        message = f"Formatting output ({', '.join(formats)})..."
        self.update_progress(ExtractionPhase.OUTPUT_FORMATTING, message, 0)
    
    def complete_output_formatting(self):
        """Complete output formatting phase."""
        message = "Output formatting completed"
        self.update_progress(ExtractionPhase.OUTPUT_FORMATTING, message, 100)
    
    def complete_extraction(self, processing_time: float):
        """
        Complete extraction process.
        
        Args:
            processing_time: Total processing time in seconds
        """
        message = f"Extraction completed successfully in {processing_time:.2f} seconds"
        self.update_progress(ExtractionPhase.COMPLETION, message, 100)
    
    def report_error(self, error_message: str):
        """
        Report extraction error.
        
        Args:
            error_message: Error message
        """
        message = f"Extraction failed: {error_message}"
        self.update_progress(ExtractionPhase.ERROR, message, 100)
