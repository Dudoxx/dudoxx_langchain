# Dudoxx Extraction API

A REST API for the Dudoxx Extraction system that provides endpoints for extracting structured information from text documents using LLM technology.

## Features

- **Text Extraction**: Extract information from text using natural language queries
- **Multi-Query Extraction**: Process multiple extraction queries on the same text
- **File Extraction**: Extract information from uploaded files
- **Document Extraction**: Extract all information from a document using parallel processing
- **Domain Identification**: Automatically identify the most relevant domains and fields for extraction
- **Document Loaders**: Support for various document formats (DOCX, HTML, CSV, Excel, PDF, text)
- **Parallel Processing**: Option to use parallel extraction for improved performance
- **Rich Logging**: Detailed console logging with rich formatting
- **API Key Authentication**: Secure API access with API key authentication
- **Swagger Documentation**: Interactive API documentation with Swagger UI
- **Real-time Progress Updates**: Socket.IO integration for real-time extraction progress tracking

## Installation

### Prerequisites

- Python 3.9+
- pip
- Dudoxx Extraction system

### Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure the `.env.dudoxx` file is properly configured with your API key and other settings:

```
DUDOXX_BASE_URL=https://llm-proxy.dudoxx.com/v1
DUDOXX_API_KEY=your-api-key
DUDOXX_MODEL_NAME=dudoxx
DUDOXX_EMBEDDING_MODEL=embedder

# LLM Parameters
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=4000
LLM_TOP_P=1.0
LLM_FREQUENCY_PENALTY=0.0
LLM_PRESENCE_PENALTY=0.0
LLM_TIMEOUT=60

# Extraction Configuration
EXTRACTION_CHUNK_SIZE=16000
EXTRACTION_CHUNK_OVERLAP=200
EXTRACTION_MAX_CONCURRENCY=20
EXTRACTION_DEDUPLICATION_THRESHOLD=0.9
EXTRACTION_DEFAULT_OUTPUT_FORMATS=json,text,xml
EXTRACTION_INCLUDE_METADATA=true
```

## Usage

### Starting the API and Socket.IO Servers

The API consists of two servers:
- FastAPI server for handling API requests (port 8000)
- Socket.IO server for real-time progress updates (port 8001)

You can start both servers with a single command:

```bash
./run_servers.sh
```

Or start them separately:

```bash
# Start the FastAPI server
python main.py

# Start the Socket.IO server
python run_socketio.py
```

The API server will be available at `http://localhost:8000` and the Socket.IO server at `http://localhost:8001`.

### API Documentation

The API documentation is available at:

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### API Endpoints

#### Health Check

```
GET /api/v1/health
```

Returns the status of the API.

#### Text Extraction

```
POST /api/v1/extract/text
```

Extract information from text using a natural language query.

**Request Body:**

```json
{
  "text": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
  "query": "Extract patient information and diagnosis",
  "domain": "medical",
  "output_formats": ["json", "text"]
}
```

**Query Parameters:**

- `use_parallel` (boolean, default: false): Whether to use parallel extraction

**Response:**

```json
{
  "status": "success",
  "operation_type": "text_extraction",
  "domain_identification": {
    "matched_domains": [...],
    "matched_fields": [...],
    "recommended_domains": ["medical"],
    "recommended_fields": {
      "medical": ["patient_name", "date_of_birth", "diagnoses"]
    }
  },
  "extraction_result": {
    "json_output": {
      "patient_name": "John Doe",
      "date_of_birth": "05/15/1980",
      "diagnoses": ["Diabetes mellitus Type II"]
    },
    "text_output": "Patient Name: John Doe\nDate of Birth: 05/15/1980\nDiagnoses: Diabetes mellitus Type II",
    "metadata": {
      "processing_time": 1.25,
      "chunk_count": 1,
      "token_count": 50
    }
  },
  "query": "Extract patient information and diagnosis",
  "domain": "medical",
  "fields": ["patient_name", "date_of_birth", "diagnoses"]
}
```

#### Multi-Query Extraction

```
POST /api/v1/extract/multi-query
```

Extract information from text using multiple queries.

**Request Body:**

```json
{
  "text": "Patient: John Doe\nDOB: 05/15/1980\nDiagnosis: Diabetes mellitus Type II",
  "queries": [
    "Extract patient information",
    "Extract diagnosis information"
  ],
  "domain": "medical",
  "output_formats": ["json", "text"]
}
```

**Query Parameters:**

- `use_parallel` (boolean, default: false): Whether to use parallel extraction

**Response:**

```json
{
  "status": "success",
  "operation_type": "multi_query_extraction",
  "domain_identification": {...},
  "extraction_result": {
    "json_output": {
      "Extract patient information": {
        "patient_name": "John Doe",
        "date_of_birth": "05/15/1980"
      },
      "Extract diagnosis information": {
        "diagnoses": ["Diabetes mellitus Type II"]
      }
    },
    "text_output": "...",
    "metadata": {
      "query_count": 2,
      "processing_time": 2.5
    }
  },
  "queries": [
    "Extract patient information",
    "Extract diagnosis information"
  ],
  "domain": "medical",
  "fields": ["patient_name", "date_of_birth", "diagnoses"]
}
```

#### File Extraction

```
POST /api/v1/extract/file
```

Extract information from an uploaded file.

**Form Data:**

- `file`: File to extract from
- `query`: Query describing what to extract
- `domain` (optional): Domain to use for extraction
- `output_formats` (optional): Comma-separated list of output formats
- `use_parallel` (boolean, default: false): Whether to use parallel extraction

**Response:**

```json
{
  "status": "success",
  "operation_type": "file_extraction",
  "domain_identification": {...},
  "extraction_result": {
    "json_output": {...},
    "text_output": "...",
    "metadata": {...}
  },
  "query": "Extract all parties involved in the contract",
  "domain": "legal",
  "fields": ["parties"]
}
```

#### Document Extraction

```
POST /api/v1/extract/document
```

Extract all information from a document using the parallel extraction pipeline.

**Form Data:**

- `file`: File to extract from
- `domain`: Domain to use for extraction
- `output_formats` (optional): Comma-separated list of output formats

**Response:**

```json
{
  "status": "success",
  "operation_type": "file_extraction",
  "extraction_result": {
    "json_output": {
      "agreement_info": {...},
      "parties": [...],
      "obligations": [...],
      "payment_terms": {...},
      "termination_provisions": [...],
      "confidentiality_provisions": {...}
    },
    "text_output": "...",
    "metadata": {...}
  },
  "domain": "legal"
}
```

### Authentication

All API endpoints (except `/api/v1/health`) require an API key for authentication. The API key should be provided in the `X-API-Key` header.

Example:

```bash
curl -X POST "http://localhost:8000/api/v1/extract/text" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"text": "Patient: John Doe\nDOB: 05/15/1980", "query": "Extract patient information"}'
```

### Real-time Progress Updates

The API provides real-time progress updates during extraction using Socket.IO. Clients can connect to the Socket.IO server at `http://localhost:8001` and listen for `progress` events.

Example using JavaScript:

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8001');

socket.on('connect', () => {
  console.log('Connected to Socket.IO server');
});

socket.on('progress', (data) => {
  console.log('Progress update:', data);
  // data = { status: 'processing', message: 'Extracting information...', percentage: 50 }
});

socket.on('disconnect', () => {
  console.log('Disconnected from Socket.IO server');
});
```

Progress updates include:
- `status`: Current status of the extraction ('starting', 'processing', 'completed', 'error')
- `message`: Human-readable progress message
- `percentage`: Optional percentage of completion (0-100)

### Client Example

A client example is provided in the `api_client_example.py` file. This script demonstrates how to use the API to extract information from text and files.

```bash
python api_client_example.py
```

The client example demonstrates:

1. Text extraction with a single query
2. Text extraction with multiple queries
3. File extraction
4. Document extraction using parallel processing
5. Text extraction with parallel processing

## Configuration

The API is configured using the `.env.dudoxx` file. See the [Setup](#setup) section for details.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DUDOXX_BASE_URL | Base URL for the LLM API | https://llm-proxy.dudoxx.com/v1 |
| DUDOXX_API_KEY | API key for authentication | (required) |
| DUDOXX_MODEL_NAME | Model name to use | dudoxx |
| DUDOXX_EMBEDDING_MODEL | Embedding model to use | embedder |
| LLM_TEMPERATURE | Temperature for LLM | 0 |
| LLM_MAX_TOKENS | Maximum tokens for LLM | 4000 |
| EXTRACTION_CHUNK_SIZE | Size of chunks for extraction | 16000 |
| EXTRACTION_CHUNK_OVERLAP | Overlap between chunks | 200 |
| EXTRACTION_MAX_CONCURRENCY | Maximum concurrent extractions | 20 |
| LOG_RICH_ENABLED | Whether to use rich logging | true |

## Development

### Project Structure

```
dudoxx_extraction_api/
├── __init__.py           # Package initialization
├── config.py             # Configuration module
├── main.py               # Main application (FastAPI server)
├── models.py             # Pydantic models
├── routes.py             # API routes
├── utils.py              # Utility functions
├── socket_manager.py     # Socket.IO manager
├── run_socketio.py       # Socket.IO server
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

### Key Components

- **config.py**: Loads configuration from `.env.dudoxx` file
- **models.py**: Defines request and response models using Pydantic
- **routes.py**: Implements API endpoints using FastAPI
- **utils.py**: Provides utility functions for domain identification and extraction
- **main.py**: Sets up the FastAPI application and includes routes
- **socket_manager.py**: Manages Socket.IO connections and events
- **run_socketio.py**: Runs the Socket.IO server

### Adding New Endpoints

To add a new endpoint:

1. Define the request and response models in `models.py`
2. Add the endpoint handler in `routes.py`
3. Implement any necessary utility functions in `utils.py`
4. Update the documentation in this README

### Error Handling

The API includes comprehensive error handling:

- API key validation
- Request validation
- Domain and field identification errors
- Extraction errors
- File handling errors

All errors are logged with detailed information and returned to the client with appropriate status codes and error messages.

## License

This project is licensed under the MIT License.
