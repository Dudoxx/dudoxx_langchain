"""
DOCX document loader for the Dudoxx Extraction system.

This module provides a document loader for DOCX files using LangChain's document loaders.
"""

from typing import List, Optional
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.documents import Document


class DocxLoader:
    """
    Document loader for DOCX files.

    This class wraps LangChain's Docx2txtLoader to provide a consistent interface
    for loading DOCX files in the Dudoxx Extraction system.

    Attributes:
        file_path (str): Path to the DOCX file.
        loader (Docx2txtLoader): LangChain's DOCX loader.
    """

    def __init__(self, file_path: str):
        """
        Initialize the DOCX loader.

        Args:
            file_path (str): Path to the DOCX file.
        """
        self.file_path = file_path
        self.loader = Docx2txtLoader(file_path)

    def load(self) -> List[Document]:
        """
        Load the DOCX file and return a list of documents.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        return self.loader.load()

    def load_and_split(self, text_splitter) -> List[Document]:
        """
        Load the DOCX file, split it using the provided text splitter, and return a list of documents.

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
        Check if the file is a supported DOCX file.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is a supported DOCX file, False otherwise.
        """
        return file_path.lower().endswith(".docx")
