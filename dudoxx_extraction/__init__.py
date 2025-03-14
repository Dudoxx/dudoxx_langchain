"""
Dudoxx Extraction - Automated Large-Text Field Extraction Solution

This package provides a solution for extracting structured information from large text documents
using LangChain components and Large Language Models (LLMs).
"""

__version__ = "1.0.0"

# Import main components
from .extraction_pipeline import (
    ExtractionPipeline,
    TemporalNormalizer,
    ResultMerger,
    OutputFormatter,
    extract_text,
    extract_file
)
from .client import ExtractionClient, ExtractionClientSync

# Export main components
__all__ = [
    "ExtractionPipeline",
    "TemporalNormalizer",
    "ResultMerger",
    "OutputFormatter",
    "ExtractionClient",
    "ExtractionClientSync",
    "extract_text",
    "extract_file"
]
