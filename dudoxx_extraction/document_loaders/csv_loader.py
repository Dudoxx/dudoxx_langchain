"""
CSV document loader for the Dudoxx Extraction system.

This module provides a document loader for CSV files using LangChain's document loaders.
"""

from typing import List, Optional, Dict, Any
from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document


class CsvLoader:
    """
    Document loader for CSV files.

    This class wraps LangChain's CSVLoader to provide a consistent interface
    for loading CSV files in the Dudoxx Extraction system.

    Attributes:
        file_path (str): Path to the CSV file.
        loader (CSVLoader): LangChain's CSV loader.
    """

    def __init__(
        self,
        file_path: str,
        csv_args: Optional[Dict[str, Any]] = None,
        source_column: Optional[str] = None,
        metadata_columns: Optional[List[str]] = None,
        encoding: Optional[str] = None,
    ):
        """
        Initialize the CSV loader.

        Args:
            file_path (str): Path to the CSV file.
            csv_args (Optional[Dict[str, Any]]): Arguments to pass to the CSV reader.
            source_column (Optional[str]): Column to use as the source.
            metadata_columns (Optional[List[str]]): Columns to use as metadata.
            encoding (Optional[str]): Encoding to use when opening the file.
        """
        self.file_path = file_path
        self.loader = CSVLoader(
            file_path=file_path,
            csv_args=csv_args,
            source_column=source_column,
            metadata_columns=metadata_columns,
            encoding=encoding,
        )

    def load(self) -> List[Document]:
        """
        Load the CSV file and return a list of documents.

        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        return self.loader.load()

    def load_and_split(self, text_splitter) -> List[Document]:
        """
        Load the CSV file, split it using the provided text splitter, and return a list of documents.

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
        Check if the file is a supported CSV file.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is a supported CSV file, False otherwise.
        """
        return file_path.lower().endswith(".csv")
