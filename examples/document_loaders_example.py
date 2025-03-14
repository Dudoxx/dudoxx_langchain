"""
Example script demonstrating the use of document loaders in the Dudoxx Extraction system.

This script shows how to use the document loaders to load and process various file formats.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console
from rich.panel import Panel

from dudoxx_extraction.document_loaders import (
    DocxLoader,
    HtmlLoader,
    CsvLoader,
    ExcelLoader,
    OcrPdfLoader,
    DocumentLoaderFactory,
)


def create_example_files():
    """Create example files for demonstration purposes."""
    examples_dir = Path("examples/files")
    examples_dir.mkdir(exist_ok=True, parents=True)

    # Create a simple DOCX-like text file (not a real DOCX)
    with open(examples_dir / "example.docx.txt", "w") as f:
        f.write("This is an example DOCX file.\n\nIt contains some text for demonstration purposes.")

    # Create a simple HTML file
    with open(examples_dir / "example.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Example HTML</title>
</head>
<body>
    <h1>Example HTML File</h1>
    <p>This is an example HTML file for demonstration purposes.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
</body>
</html>""")

    # Create a simple CSV file
    with open(examples_dir / "example.csv", "w") as f:
        f.write("""Name,Age,City
John Doe,30,New York
Jane Smith,25,Los Angeles
Bob Johnson,40,Chicago""")

    # Create a simple text file to simulate a PDF
    with open(examples_dir / "example.pdf.txt", "w") as f:
        f.write("This is an example PDF file.\n\nIt contains some text for demonstration purposes.")

    return examples_dir


def demonstrate_document_loaders():
    """Demonstrate the use of document loaders."""
    console = Console()
    examples_dir = create_example_files()

    # Create a text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )

    # Demonstrate loading HTML
    console.print(Panel("Loading HTML file", style="cyan"))
    html_file = examples_dir / "example.html"
    try:
        html_loader = HtmlLoader(str(html_file))
        html_docs = html_loader.load()
        console.print(f"Loaded {len(html_docs)} documents from HTML file")
        for i, doc in enumerate(html_docs):
            console.print(f"Document {i+1} content (first 100 chars): {doc.page_content[:100]}...")
            console.print(f"Document {i+1} metadata: {doc.metadata}")
    except Exception as e:
        console.print(f"Error loading HTML file: {e}", style="red")

    # Demonstrate loading CSV
    console.print(Panel("Loading CSV file", style="cyan"))
    csv_file = examples_dir / "example.csv"
    try:
        csv_loader = CsvLoader(str(csv_file))
        csv_docs = csv_loader.load()
        console.print(f"Loaded {len(csv_docs)} documents from CSV file")
        for i, doc in enumerate(csv_docs):
            console.print(f"Document {i+1} content (first 100 chars): {doc.page_content[:100]}...")
            console.print(f"Document {i+1} metadata: {doc.metadata}")
    except Exception as e:
        console.print(f"Error loading CSV file: {e}", style="red")

    # Demonstrate using the DocumentLoaderFactory
    console.print(Panel("Using DocumentLoaderFactory", style="cyan"))
    for file_path in examples_dir.glob("*"):
        if DocumentLoaderFactory.is_supported_file(str(file_path)):
            console.print(f"File {file_path.name} is supported")
        else:
            console.print(f"File {file_path.name} is not supported")

    # Demonstrate loading and splitting a document
    console.print(Panel("Loading and splitting a document", style="cyan"))
    try:
        html_docs_split = DocumentLoaderFactory.load_and_split_document(
            str(html_file), text_splitter
        )
        console.print(f"Loaded and split into {len(html_docs_split)} chunks")
        for i, doc in enumerate(html_docs_split):
            console.print(f"Chunk {i+1} content (first 100 chars): {doc.page_content[:100]}...")
    except Exception as e:
        console.print(f"Error loading and splitting document: {e}", style="red")


if __name__ == "__main__":
    demonstrate_document_loaders()
