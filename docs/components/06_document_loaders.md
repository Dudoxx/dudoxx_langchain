# Document Loaders

The `document_loaders` module provides a set of document loaders for various file formats, enabling the Dudoxx Extraction system to process different types of documents.

## Overview

Document loaders are responsible for loading documents from various file formats and converting them into a standardized format that can be processed by the extraction pipeline. The Dudoxx Extraction system supports several file formats, including DOCX, HTML, CSV, Excel, and scanned PDFs with OCR.

## Key Components

The document loaders module consists of the following components:

1. **DocxLoader**: Loads DOCX files using LangChain's Docx2txtLoader
2. **HtmlLoader**: Loads HTML files using LangChain's BSHTMLLoader
3. **CsvLoader**: Loads CSV files using LangChain's CSVLoader
4. **ExcelLoader**: Loads Excel files using LangChain's UnstructuredExcelLoader
5. **OcrPdfLoader**: Loads scanned PDF files using LangChain's UnstructuredPDFLoader with OCR capabilities
6. **DocumentLoaderFactory**: Factory class for creating document loaders based on file extensions

## Implementation

Each document loader is implemented as a wrapper around a LangChain document loader, providing a consistent interface for loading documents in the Dudoxx Extraction system.

### Common Interface

All document loaders implement the following interface:

```python
def load() -> List[Document]:
    """
    Load the document and return a list of documents.
    
    Returns:
        List[Document]: A list of LangChain Document objects.
    """
    pass

def load_and_split(text_splitter) -> List[Document]:
    """
    Load the document, split it using the provided text splitter, and return a list of documents.
    
    Args:
        text_splitter: A LangChain text splitter.
        
    Returns:
        List[Document]: A list of LangChain Document objects.
    """
    pass

@staticmethod
def is_supported_file(file_path: str) -> bool:
    """
    Check if the file is supported by this loader.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        bool: True if the file is supported, False otherwise.
    """
    pass
```

### Document Loader Factory

The `DocumentLoaderFactory` class provides a convenient way to create document loaders based on file extensions:

```python
class DocumentLoaderFactory:
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
        pass
    
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
        pass
    
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
        pass
    
    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """
        Check if the file is supported by any of the available loaders.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            bool: True if the file is supported, False otherwise.
        """
        pass
```

## Usage Example

Here's an example of how to use the document loaders:

```python
from dudoxx_extraction.document_loaders import DocumentLoaderFactory
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create a text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
)

# Load a document
file_path = "example.html"
if DocumentLoaderFactory.is_supported_file(file_path):
    # Load the document
    docs = DocumentLoaderFactory.load_document(file_path)
    print(f"Loaded {len(docs)} documents")
    
    # Load and split the document
    docs_split = DocumentLoaderFactory.load_and_split_document(file_path, text_splitter)
    print(f"Loaded and split into {len(docs_split)} chunks")
else:
    print(f"File {file_path} is not supported")
```

## Integration with Extraction Pipeline

The document loaders are integrated into the extraction pipeline and are used to load documents for processing:

```python
# In ExtractionPipeline.process_document
def process_document(self, document_path, fields, domain, output_formats=["json", "text"]):
    # Step 1: Load document
    if self.logger:
        self.logger.log_step("Document Loading", f"Loading document from {document_path}")
    
    docs = DocumentLoaderFactory.load_document(document_path)
    
    # Step 2: Split document into chunks
    if self.logger:
        self.logger.log_step("Document Chunking", "Splitting document into chunks")
    
    chunks = self.text_splitter.split_documents(docs)
    
    # ... rest of the pipeline
```

## Benefits

1. **Flexibility**: Support for various file formats allows the system to process different types of documents.
2. **Consistency**: All document loaders provide a consistent interface, making it easy to add support for new file formats.
3. **Integration**: Seamless integration with LangChain's document loaders leverages existing functionality.
4. **Extensibility**: The factory pattern makes it easy to add support for new file formats.
5. **Convenience**: The factory class provides a convenient way to create document loaders based on file extensions.

## Customization

The document loaders can be customized in several ways:

1. **Additional File Formats**: Add support for additional file formats by creating new document loader classes.
2. **Custom Loaders**: Create custom document loaders for specific use cases.
3. **Configuration Options**: Customize the behavior of document loaders through configuration options.
4. **Pre/Post Processing**: Add pre-processing or post-processing steps to the document loading process.
5. **Error Handling**: Customize error handling for document loading errors.
