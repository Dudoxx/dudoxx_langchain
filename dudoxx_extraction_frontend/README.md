# Dudoxx Extraction Frontend

A web-based frontend for the Dudoxx Extraction API that provides a user-friendly interface for extracting structured information from text documents.

## Features

- **User Authentication**: Secure access with API key authentication
- **Text Extraction**: Extract information from text using natural language queries
- **File Extraction**: Extract information from uploaded files (TXT, PDF, DOCX, HTML, CSV)
- **Multi-Query Extraction**: Process multiple extraction queries on the same text
- **Domain Identification**: Automatically identify the most relevant domains and fields
- **Parallel Processing**: Option to use parallel extraction for improved performance
- **Real-time Progress Tracking**: Monitor extraction progress in real-time
- **Result Visualization**: View extraction results in JSON, text, and metadata formats
- **Responsive Design**: Works on desktop and mobile devices

## Installation

### Prerequisites

- Node.js 14+
- npm or yarn
- Dudoxx Extraction API running

### Setup

1. Install dependencies:

```bash
cd dudoxx_extraction_frontend
npm install
```

2. Create a `.env` file with the following configuration:

```
PORT=3000
API_BASE_URL=http://localhost:8000/api/v1
SESSION_SECRET=your-session-secret
```

3. Start the server:

```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

## Usage

### Authentication

1. Access the frontend at `http://localhost:3000`
2. Enter your Dudoxx Extraction API key on the login page
3. After successful authentication, you'll be redirected to the dashboard

### Text Extraction

1. Navigate to the "Extract" page
2. Select the "Text Extraction" tab
3. Enter your query (e.g., "Extract all parties involved in the contract")
4. Paste the text content
5. Optionally select a domain or enable parallel processing
6. Click "Extract Information"
7. View the extraction results

### File Extraction

1. Navigate to the "Extract" page
2. Select the "File Extraction" tab
3. Enter your query
4. Upload a file (supported formats: TXT, PDF, DOCX, HTML, CSV)
5. Optionally select a domain or enable parallel processing
6. Click "Extract Information"
7. View the extraction results

### Multi-Query Extraction

1. Navigate to the "Extract" page
2. Select the "Multi-Query Extraction" tab
3. Enter multiple queries (one per line)
4. Paste the text content
5. Optionally select a domain or enable parallel processing
6. Click "Extract Information"
7. View the extraction results for all queries

## Project Structure

```
dudoxx_extraction_frontend/
├── public/                # Static assets
│   ├── css/               # CSS stylesheets
│   │   └── styles.css     # Custom styles
│   └── js/                # JavaScript files
│       ├── main.js        # Common functionality
│       └── extract.js     # Extraction functionality
├── views/                 # EJS templates
│   ├── layout.ejs         # Layout template
│   ├── login.ejs          # Login page
│   ├── dashboard.ejs      # Dashboard page
│   ├── extract.ejs        # Extraction page
│   ├── results.ejs        # Results page
│   └── error.ejs          # Error page
├── uploads/               # Temporary file uploads
├── server.js              # Express server
├── package.json           # Dependencies
└── README.md              # Documentation
```

## Technologies Used

- **Express.js**: Web server framework
- **EJS**: Templating engine
- **Socket.io**: Real-time communication
- **Bootstrap**: UI framework
- **Axios**: HTTP client
- **Multer**: File upload handling

## Security Considerations

- API keys are stored in server-side sessions, not in browser storage
- All API requests are proxied through the backend to avoid exposing the API key to the client
- Session data is encrypted using a secret key
- File uploads are validated and stored in a temporary directory
- Temporary files are automatically deleted after processing

## License

This project is licensed under the MIT License.
