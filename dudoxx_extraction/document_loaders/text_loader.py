"""
Text Loader for Dudoxx Extraction

This module provides a loader for plain text files.
"""

import os
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.document_loaders.base import BaseLoader
from langchain_text_splitters import TextSplitter


class TextLoader(BaseLoader):
    """Loader for plain text files."""

    def __init__(self, file_path: str):
        """Initialize with file path."""
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")

    def load(self) -> List[Document]:
        """Load and return documents from the file."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()

        metadata = {"source": self.file_path}
        return [Document(page_content=text, metadata=metadata)]

    def load_and_split(self, text_splitter: TextSplitter) -> List[Document]:
        """Load and split documents from the file."""
        docs = self.load()
        return text_splitter.split_documents(docs)
