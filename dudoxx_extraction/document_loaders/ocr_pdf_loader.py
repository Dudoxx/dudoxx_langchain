"""
OCR PDF document loader for the Dudoxx Extraction system.

This module provides a document loader for scanned PDF files using LangChain's document loaders
with OCR (Optical Character Recognition) capabilities.
"""

from typing import List, Optional, Union, Sequence, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, PyPDFium2Loader
from langchain_core.documents import Document
import logging

# Set up logging
logger = logging.getLogger(__name__)


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
        
        try:
            # Use PyPDFLoader as the primary loader
            self.loader = PyPDFLoader(file_path=file_path)
            logger.info(f"Using PyPDFLoader for {file_path}")
        except Exception as e:
            logger.warning(f"PyPDFLoader failed: {e}. Falling back to PyPDFium2Loader.")
            # Fallback to PyPDFium2Loader
            self.loader = PyPDFium2Loader(file_path=file_path)

    def load(self) -> List[Document]:
        """
        Load the PDF file and return a list of documents.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        return self.loader.load()

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
