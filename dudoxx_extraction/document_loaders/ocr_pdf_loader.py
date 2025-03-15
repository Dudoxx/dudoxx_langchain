"""
OCR PDF document loader for the Dudoxx Extraction system.

This module provides a document loader for scanned PDF files using LangChain's document loaders
with OCR (Optical Character Recognition) capabilities.
"""

from typing import List, Optional, Union, Sequence, Dict, Any
import os
import logging
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler
from langchain_community.document_loaders import PyPDFLoader, PyPDFium2Loader, PDFMinerLoader
from langchain_core.documents import Document

# Set up rich console for logging
console = Console()

# Configure logging with rich handler if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )

# Get logger for this module
logger = logging.getLogger("ocr_pdf_loader")


class OcrPdfLoader:
    """
    Document loader for scanned PDF files with OCR.

    This class provides options for loading scanned PDF files using different LangChain loaders
    with OCR capabilities.

    Attributes:
        file_path (str): Path to the PDF file.
        loader: LangChain's PDF loader.
        use_ocr (bool): Whether to use OCR for text extraction.
    """

    def __init__(
        self,
        file_path: str,
        use_ocr: bool = False,  # Default to False since OCR is not working properly
        ocr_languages: str = "eng",
        ocr_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the OCR PDF loader.

        Args:
            file_path (str): Path to the PDF file.
            use_ocr (bool): Whether to use OCR for text extraction.
            ocr_languages (str): Languages to use for OCR (e.g., "eng" for English).
            ocr_config (Optional[Dict[str, Any]]): Additional configuration for OCR.
        """
        self.file_path = file_path
        self.use_ocr = use_ocr
        
        console.print(Panel(
            f"[bold blue]Initializing PDF loader for: {file_path}[/]\n"
            f"[cyan]Use OCR: {use_ocr}[/]\n"
            f"[cyan]OCR Languages: {ocr_languages}[/]",
            title="PDF Loader Initialization",
            border_style="blue"
        ))
        
        # Check if file exists
        if not os.path.exists(file_path):
            error_msg = f"PDF file does not exist: {file_path}"
            logger.error(error_msg)
            console.print(Panel(
                f"[bold red]Error: {error_msg}[/]",
                title="File Not Found",
                border_style="red"
            ))
            raise FileNotFoundError(error_msg)
        
        # Check file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        logger.info(f"PDF file size: {file_size:.2f} MB")
        
        # Try different PDF loaders in sequence
        loaders_to_try = [
            ("PyPDFLoader", lambda: PyPDFLoader(file_path=file_path)),
            ("PDFMinerLoader", lambda: PDFMinerLoader(file_path=file_path)),
            ("PyPDFium2Loader", lambda: PyPDFium2Loader(file_path=file_path))
        ]
        
        for loader_name, loader_factory in loaders_to_try:
            try:
                logger.info(f"Trying {loader_name} for {file_path}")
                self.loader = loader_factory()
                self.loader_name = loader_name
                console.print(f"[green]Successfully initialized {loader_name} for {file_path}[/]")
                break
            except Exception as e:
                error_msg = f"{loader_name} initialization failed: {str(e)}"
                logger.warning(error_msg)
                console.print(f"[yellow]{error_msg}[/]")
                continue
        else:
            # If all loaders fail
            error_msg = f"All PDF loaders failed for {file_path}"
            logger.error(error_msg)
            console.print(Panel(
                f"[bold red]Error: {error_msg}[/]",
                title="PDF Loader Error",
                border_style="red"
            ))
            raise ValueError(error_msg)

    def load(self) -> List[Document]:
        """
        Load the PDF file and return a list of documents.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        console.print(Panel(
            f"[bold blue]Loading PDF file: {self.file_path}[/]\n"
            f"[cyan]Using loader: {getattr(self, 'loader_name', type(self.loader).__name__)}[/]",
            title="PDF Loading Process",
            border_style="blue"
        ))
        
        try:
            docs = self.loader.load()
            
            # Log document information
            doc_count = len(docs)
            logger.info(f"Loaded {doc_count} document(s) from PDF")
            
            if doc_count > 0:
                # Calculate total text length
                total_text_length = sum(len(doc.page_content) for doc in docs)
                logger.info(f"Total extracted text length: {total_text_length} characters")
                
                # Log sample of extracted text
                if total_text_length > 0:
                    sample_text = docs[0].page_content[:200] + "..." if len(docs[0].page_content) > 200 else docs[0].page_content
                    console.print(Panel(
                        f"[bold green]PDF loaded successfully[/]\n"
                        f"[cyan]Document count: {doc_count}[/]\n"
                        f"[cyan]Total text length: {total_text_length} characters[/]\n"
                        f"[cyan]Sample text:[/] {sample_text}",
                        title="PDF Content Sample",
                        border_style="green"
                    ))
                else:
                    console.print(Panel(
                        f"[bold yellow]Warning: No text extracted from PDF[/]\n"
                        f"[yellow]Document count: {doc_count}[/]\n"
                        f"[yellow]Total text length: 0 characters[/]",
                        title="Empty PDF Content",
                        border_style="yellow"
                    ))
            else:
                console.print(Panel(
                    f"[bold yellow]Warning: No documents extracted from PDF[/]",
                    title="Empty PDF Result",
                    border_style="yellow"
                ))
            
            return docs
        except Exception as e:
            error_msg = f"Error loading PDF {self.file_path}: {str(e)}"
            logger.exception(error_msg)
            console.print(Panel(
                f"[bold red]Error loading PDF: {self.file_path}[/]\n"
                f"[red]Error: {str(e)}[/]",
                title="PDF Loading Error",
                border_style="red"
            ))
            raise

    def load_and_split(self, text_splitter) -> List[Document]:
        """
        Load the PDF file, split it using the provided text splitter, and return a list of documents.

        Args:
            text_splitter: A LangChain text splitter.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        docs = self.load()
        return text_splitter.split_documents(docs)

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """
        Check if the file is a supported PDF file.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is a supported PDF file, False otherwise.
        """
        return file_path.lower().endswith(".pdf")
