# Dudoxx Extraction Documentation

This directory contains comprehensive documentation for the Dudoxx Extraction system, a robust solution for extracting structured information from large text documents using LangChain components and LLM technology.

## LangChain Integration

The [LangChain Components](langchain_components.md) document provides an overview of LangChain 0.3 components that can be integrated into our document extraction system, including structured output extraction, contextual compression, and more.

## Component Documentation

The `components` directory contains detailed documentation for each major component of the system:

1. [Extraction Pipeline](components/01_extraction_pipeline.md) - The core component that orchestrates the entire extraction process
2. [Temporal Normalizer](components/02_temporal_normalizer.md) - Handles date normalization and timeline construction
3. [Result Merger](components/03_result_merger.md) - Merges and deduplicates results from multiple document chunks
4. [Output Formatter](components/04_output_formatter.md) - Formats extraction results in various output formats
5. [Rich Logger](components/05_rich_logger.md) - Provides detailed, colorful console output for better visibility
6. [Document Loaders](components/06_document_loaders.md) - Loads documents from various file formats (DOCX, HTML, CSV, Excel, PDF)

## Architecture Overview

The Dudoxx Extraction system follows a modular architecture where each component is responsible for a specific part of the extraction process. This design allows for easy customization and extension of the system.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Document       │     │  Text           │     │  LLM            │
│  Loader         │────▶│  Splitter       │────▶│  Processor      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Output         │     │  Result         │     │  Temporal       │
│  Formatter      │◀────│  Merger         │◀────│  Normalizer     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Process Flow

1. **Document Loading**: The document is loaded using the specified document loader.
2. **Document Chunking**: Large documents are split into manageable chunks.
3. **LLM Processing**: Each chunk is processed by the LLM to extract information.
4. **Temporal Normalization**: Dates and timelines are normalized for consistency.
5. **Result Merging**: Results from multiple chunks are merged and deduplicated.
6. **Output Formatting**: The final result is formatted in the requested output formats.

## Usage Examples

For usage examples, please refer to the [README.md](../README.md) file in the project root directory.

## Contributing

If you'd like to contribute to the documentation, please follow these guidelines:

1. Use Markdown for all documentation files.
2. Include code examples where appropriate.
3. Keep the documentation up-to-date with the code.
4. Add diagrams or images to illustrate complex concepts.
5. Follow the existing structure and naming conventions.

## License

This documentation is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
