"""
Setup script for the Automated Large-Text Field Extraction Solution.
"""

from setuptools import setup, find_packages

setup(
    name="dudoxx-extraction",
    version="1.0.0",
    description="Automated Large-Text Field Extraction Solution using LangChain",
    author="Dudoxx",
    author_email="info@dudoxx.ai",
    url="https://github.com/dudoxx/extraction",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.2.0",
        "langchain-community>=0.2.0",
        "langchain-openai>=0.2.0",
        "openai>=1.0.0",
        "faiss-cpu>=1.7.0",
        "numpy>=1.20.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "python-multipart>=0.0.5",
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
        "pyyaml>=6.0.0",
        "tiktoken>=0.4.0",
        "unstructured>=0.10.0",
        "pdf2image>=1.16.0",
        "pytesseract>=0.3.0",
        "python-docx>=0.8.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "dudoxx-extraction=dudoxx_extraction.cli:main",
        ],
    },
)
