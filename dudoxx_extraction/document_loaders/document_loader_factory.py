"""
Document loader factory for the Dudoxx Extraction system.

This module provides a factory for creating document loaders based on file extensions.
"""

from typing import Optional, Dict, Any, List, Type
import os
from langchain_core.documents import Document

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
        if DocxLoader.is_supported_file(file_path):
            return DocxLoader(file_path, **kwargs)
        elif HtmlLoader.is_supported_file(file_path):
            return HtmlLoader(file_path, **kwargs)
        elif CsvLoader.is_supported_file(file_path):
            return CsvLoader(file_path, **kwargs)
        elif ExcelLoader.is_supported_file(file_path):
            return ExcelLoader(file_path, **kwargs)
        elif OcrPdfLoader.is_supported_file(file_path):
            return OcrPdfLoader(file_path, **kwargs)
        else:
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
        loader = DocumentLoaderFactory.get_loader_for_file(file_path, **kwargs)
        if loader is None:
            raise ValueError(f"No loader available for file: {file_path}")
        return loader.load()

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
        return (
            DocxLoader.is_supported_file(file_path)
            or HtmlLoader.is_supported_file(file_path)
            or CsvLoader.is_supported_file(file_path)
            or ExcelLoader.is_supported_file(file_path)
            or OcrPdfLoader.is_supported_file(file_path)
        )
