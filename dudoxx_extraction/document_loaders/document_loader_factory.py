"""
Document loader factory for the Dudoxx Extraction system.

This module provides a factory for creating document loaders based on file extensions.
"""

from typing import Optional, Dict, Any, List, Type
import os
import logging
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler
from langchain_core.documents import Document

# Set up rich console for logging
console = Console()

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("document_loaders")

from dudoxx_extraction.document_loaders.docx_loader import DocxLoader
from dudoxx_extraction.document_loaders.html_loader import HtmlLoader
from dudoxx_extraction.document_loaders.csv_loader import CsvLoader
from dudoxx_extraction.document_loaders.excel_loader import ExcelLoader
from dudoxx_extraction.document_loaders.ocr_pdf_loader import OcrPdfLoader


class DocumentLoaderFactory:
    """
    Factory for creating document loaders based on file extensions.

    This class provides methods for creating document loaders for various file formats.
    """

    @staticmethod
    def get_loader_for_file(file_path: str, **kwargs) -> Optional[object]:
        """
        Get a document loader for the specified file.

        Args:
            file_path (str): Path to the file.
            **kwargs: Additional arguments to pass to the loader.

        Returns:
            Optional[object]: A document loader for the specified file, or None if no loader is available.
        """
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        console.print(Panel(
            f"[bold blue]Getting loader for file: {file_path}[/]\n"
            f"[cyan]File extension: {ext}[/]",
            title="Document Loader Factory",
            border_style="blue"
        ))
        
        if DocxLoader.is_supported_file(file_path):
            logger.info(f"Using DocxLoader for file: {file_path}")
            return DocxLoader(file_path, **kwargs)
        elif HtmlLoader.is_supported_file(file_path):
            logger.info(f"Using HtmlLoader for file: {file_path}")
            return HtmlLoader(file_path, **kwargs)
        elif CsvLoader.is_supported_file(file_path):
            logger.info(f"Using CsvLoader for file: {file_path}")
            return CsvLoader(file_path, **kwargs)
        elif ExcelLoader.is_supported_file(file_path):
            logger.info(f"Using ExcelLoader for file: {file_path}")
            return ExcelLoader(file_path, **kwargs)
        elif OcrPdfLoader.is_supported_file(file_path):
            logger.info(f"Using OcrPdfLoader for file: {file_path}")
            return OcrPdfLoader(file_path, **kwargs)
        elif ext == ".txt":
            from dudoxx_extraction.document_loaders.text_loader import TextLoader
            logger.info(f"Using TextLoader for file: {file_path}")
            return TextLoader(file_path)
        else:
            logger.warning(f"No loader available for file: {file_path}")
            return None

    @staticmethod
    def load_document(file_path: str, **kwargs) -> List[Document]:
        """
        Load a document from the specified file.

        Args:
            file_path (str): Path to the file.
            **kwargs: Additional arguments to pass to the loader.

        Returns:
            List[Document]: A list of LangChain Document objects.

        Raises:
            ValueError: If no loader is available for the specified file.
        """
        console.print(Panel(
            f"[bold green]Loading document: {file_path}[/]",
            title="Document Loader",
            border_style="green"
        ))
        
        loader = DocumentLoaderFactory.get_loader_for_file(file_path, **kwargs)
        if loader is None:
            error_msg = f"No loader available for file: {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            docs = loader.load()
            logger.info(f"Successfully loaded {len(docs)} document(s) from {file_path}")
            
            # Log a sample of the extracted text
            if docs and len(docs) > 0:
                sample_text = docs[0].page_content[:200] + "..." if len(docs[0].page_content) > 200 else docs[0].page_content
                console.print(Panel(
                    f"[bold green]Document loaded successfully[/]\n"
                    f"[cyan]Document count: {len(docs)}[/]\n"
                    f"[cyan]Sample text:[/] {sample_text}",
                    title="Document Content Sample",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold yellow]Warning: No content extracted from {file_path}[/]",
                    title="Empty Document",
                    border_style="yellow"
                ))
            
            return docs
        except Exception as e:
            error_msg = f"Error loading document {file_path}: {str(e)}"
            logger.exception(error_msg)
            console.print(Panel(
                f"[bold red]Error loading document: {file_path}[/]\n"
                f"[red]Error: {str(e)}[/]",
                title="Document Loading Error",
                border_style="red"
            ))
            raise

    @staticmethod
    def load_and_split_document(file_path: str, text_splitter, **kwargs) -> List[Document]:
        """
        Load a document from the specified file and split it using the provided text splitter.

        Args:
            file_path (str): Path to the file.
            text_splitter: A LangChain text splitter.
            **kwargs: Additional arguments to pass to the loader.

        Returns:
            List[Document]: A list of LangChain Document objects.

        Raises:
            ValueError: If no loader is available for the specified file.
        """
        loader = DocumentLoaderFactory.get_loader_for_file(file_path, **kwargs)
        if loader is None:
            raise ValueError(f"No loader available for file: {file_path}")
        return loader.load_and_split(text_splitter)

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """
        Check if the file is supported by any of the available loaders.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is supported, False otherwise.
        """
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        return (
            DocxLoader.is_supported_file(file_path)
            or HtmlLoader.is_supported_file(file_path)
            or CsvLoader.is_supported_file(file_path)
            or ExcelLoader.is_supported_file(file_path)
            or OcrPdfLoader.is_supported_file(file_path)
            or ext == ".txt"  # Add support for text files
        )
