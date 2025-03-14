"""
HTML document loader for the Dudoxx Extraction system.

This module provides a document loader for HTML files using LangChain's document loaders.
"""

from typing import List, Optional
from langchain_community.document_loaders import BSHTMLLoader
from langchain_core.documents import Document


class HtmlLoader:
    """
    Document loader for HTML files.

    This class wraps LangChain's BSHTMLLoader to provide a consistent interface
    for loading HTML files in the Dudoxx Extraction system.

    Attributes:
        file_path (str): Path to the HTML file.
        loader (BSHTMLLoader): LangChain's HTML loader.
    """

    def __init__(self, file_path: str, open_encoding: Optional[str] = None):
        """
        Initialize the HTML loader.

        Args:
            file_path (str): Path to the HTML file.
            open_encoding (Optional[str]): Encoding to use when opening the file.
        """
        self.file_path = file_path
        self.loader = BSHTMLLoader(file_path, open_encoding=open_encoding)

    def load(self) -> List[Document]:
        """
        Load the HTML file and return a list of documents.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        return self.loader.load()

    def load_and_split(self, text_splitter) -> List[Document]:
        """
        Load the HTML file, split it using the provided text splitter, and return a list of documents.

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
        Check if the file is a supported HTML file.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is a supported HTML file, False otherwise.
        """
        return file_path.lower().endswith((".html", ".htm"))
