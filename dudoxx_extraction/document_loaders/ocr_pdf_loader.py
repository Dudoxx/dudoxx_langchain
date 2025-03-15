"""
OCR PDF document loader for the Dudoxx Extraction system.

This module provides a document loader for scanned PDF files using LangChain's document loaders
with OCR (Optical Character Recognition) capabilities.
"""

from typing import List, Optional, Union, Sequence, Dict, Any
import os
import io
import tempfile
import logging
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler
from langchain_community.document_loaders import PyPDFLoader, PyPDFium2Loader, PDFMinerLoader
from langchain_core.documents import Document

# Import OCR libraries
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    HAS_OCR_DEPS = True
except ImportError:
    HAS_OCR_DEPS = False
    pass

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
        use_ocr: bool = True,  # Default to True to enable OCR when needed
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
        self.ocr_languages = ocr_languages
        self.ocr_config = ocr_config or {}
        self.force_ocr = False  # Will be set to True if regular extraction yields no text
        
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
        
        # Check if OCR dependencies are available
        if not HAS_OCR_DEPS and use_ocr:
            logger.warning("OCR dependencies not available. Install pytesseract, pdf2image, and Pillow to use OCR.")
            console.print("[yellow]Warning: OCR dependencies not available. Install pytesseract, pdf2image, and Pillow to use OCR.[/]")

    def _extract_text_with_ocr(self) -> List[Document]:
        """
        Extract text from PDF using OCR.
        
        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        if not HAS_OCR_DEPS:
            logger.error("OCR dependencies not available. Cannot perform OCR.")
            console.print("[red]Error: OCR dependencies not available. Cannot perform OCR.[/]")
            return []
        
        console.print(Panel(
            f"[bold blue]Performing OCR on PDF: {self.file_path}[/]\n"
            f"[cyan]OCR Languages: {self.ocr_languages}[/]",
            title="OCR Processing",
            border_style="blue"
        ))
        
        try:
            # Convert PDF to images
            logger.info(f"Converting PDF to images for OCR")
            images = convert_from_path(self.file_path)
            
            # Process each page with OCR
            documents = []
            for i, image in enumerate(images):
                # Create a temporary file for the image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image_path = temp_file.name
                    image.save(image_path, 'PNG')
                
                try:
                    # Extract text using pytesseract
                    logger.info(f"Processing page {i+1}/{len(images)} with OCR")
                    text = pytesseract.image_to_string(
                        Image.open(image_path),
                        lang=self.ocr_languages,
                        config=self.ocr_config.get('config', '')
                    )
                    
                    # Create document
                    if text.strip():
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": self.file_path,
                                "page": i + 1,
                                "total_pages": len(images),
                                "extraction_method": "ocr"
                            }
                        )
                        documents.append(doc)
                finally:
                    # Clean up temporary file
                    if os.path.exists(image_path):
                        os.remove(image_path)
            
            # Log OCR results
            doc_count = len(documents)
            total_text_length = sum(len(doc.page_content) for doc in documents)
            
            logger.info(f"OCR extracted {doc_count} pages with {total_text_length} total characters")
            
            if doc_count > 0 and total_text_length > 0:
                sample_text = documents[0].page_content[:200] + "..." if len(documents[0].page_content) > 200 else documents[0].page_content
                console.print(Panel(
                    f"[bold green]OCR completed successfully[/]\n"
                    f"[cyan]Document count: {doc_count}[/]\n"
                    f"[cyan]Total text length: {total_text_length} characters[/]\n"
                    f"[cyan]Sample text:[/] {sample_text}",
                    title="OCR Results",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold yellow]Warning: OCR extracted no text[/]",
                    title="Empty OCR Result",
                    border_style="yellow"
                ))
            
            return documents
        except Exception as e:
            error_msg = f"Error performing OCR on {self.file_path}: {str(e)}"
            logger.exception(error_msg)
            console.print(Panel(
                f"[bold red]Error performing OCR: {self.file_path}[/]\n"
                f"[red]Error: {str(e)}[/]",
                title="OCR Error",
                border_style="red"
            ))
            return []

    def load(self) -> List[Document]:
        """
        Load the PDF file and return a list of documents.
        
        If regular text extraction yields no text and OCR is enabled,
        it will fall back to OCR-based extraction.

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
            # First try regular extraction
            docs = self.loader.load()
            
            # Log document information
            doc_count = len(docs)
            logger.info(f"Loaded {doc_count} document(s) from PDF")
            
            # Calculate total text length
            total_text_length = sum(len(doc.page_content) for doc in docs)
            logger.info(f"Total extracted text length: {total_text_length} characters")
            
            # Check if we need to use OCR
            if (total_text_length == 0 or self.force_ocr) and self.use_ocr and HAS_OCR_DEPS:
                console.print(Panel(
                    f"[bold yellow]No text extracted with regular loader. Trying OCR...[/]",
                    title="Falling Back to OCR",
                    border_style="yellow"
                ))
                
                # Try OCR extraction
                ocr_docs = self._extract_text_with_ocr()
                
                # If OCR extraction was successful, use those documents
                if ocr_docs and sum(len(doc.page_content) for doc in ocr_docs) > 0:
                    docs = ocr_docs
                    doc_count = len(docs)
                    total_text_length = sum(len(doc.page_content) for doc in docs)
                    logger.info(f"Using OCR results: {doc_count} documents, {total_text_length} characters")
            
            # Log results
            if doc_count > 0:
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
