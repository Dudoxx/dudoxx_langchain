"""
Document loaders for various file formats.

This module provides document loaders for various file formats, including:
- DOCX files
- HTML files
- CSV/Excel files
- Scanned PDFs with OCR
- Plain text files
"""

from dudoxx_extraction.document_loaders.docx_loader import DocxLoader
from dudoxx_extraction.document_loaders.html_loader import HtmlLoader
from dudoxx_extraction.document_loaders.csv_loader import CsvLoader
from dudoxx_extraction.document_loaders.excel_loader import ExcelLoader
from dudoxx_extraction.document_loaders.ocr_pdf_loader import OcrPdfLoader
from dudoxx_extraction.document_loaders.text_loader import TextLoader
from dudoxx_extraction.document_loaders.document_loader_factory import DocumentLoaderFactory

__all__ = [
    "DocxLoader",
    "HtmlLoader",
    "CsvLoader",
    "ExcelLoader",
    "OcrPdfLoader",
    "TextLoader",
    "DocumentLoaderFactory",
]
