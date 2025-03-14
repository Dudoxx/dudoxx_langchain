"""
Excel document loader for the Dudoxx Extraction system.

This module provides a document loader for Excel files using LangChain's document loaders.
"""

from typing import List, Optional, Union, Sequence
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_core.documents import Document


class ExcelLoader:
    """
    Document loader for Excel files.

    This class wraps LangChain's UnstructuredExcelLoader to provide a consistent interface
    for loading Excel files in the Dudoxx Extraction system.

    Attributes:
        file_path (str): Path to the Excel file.
        loader (UnstructuredExcelLoader): LangChain's Excel loader.
    """

    def __init__(
        self,
        file_path: str,
        mode: str = "single",
        sheet_name: Optional[Union[str, int, Sequence]] = None,
    ):
        """
        Initialize the Excel loader.

        Args:
            file_path (str): Path to the Excel file.
            mode (str): Mode to use for loading. Either "single" or "elements".
            sheet_name (Optional[Union[str, int, Sequence]]): Sheet name(s) to load.
        """
        self.file_path = file_path
        self.loader = UnstructuredExcelLoader(
            file_path=file_path,
            mode=mode,
        )
        self.sheet_name = sheet_name

    def load(self) -> List[Document]:
        """
        Load the Excel file and return a list of documents.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        return self.loader.load()

    def load_and_split(self, text_splitter) -> List[Document]:
        """
        Load the Excel file, split it using the provided text splitter, and return a list of documents.

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
        Check if the file is a supported Excel file.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is a supported Excel file, False otherwise.
        """
        return file_path.lower().endswith((".xlsx", ".xls", ".xlsm"))
