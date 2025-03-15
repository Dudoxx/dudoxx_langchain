"""
Main application for the Dudoxx Extraction API.

This module initializes the FastAPI application and includes the API routes.
"""

import os
import sys
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Dudoxx Extraction components
from dudoxx_extraction.domains.domain_init import initialize_domains

# Import API components
from dudoxx_extraction_api.config import API_TITLE, API_DESCRIPTION, API_VERSION
from dudoxx_extraction_api.routes import router
from dudoxx_extraction_api.progress_manager import get_active_connections_count, get_active_requests_count

# Initialize console for logging
console = Console()

# Initialize domains
initialize_domains()

# Define lifespan context manager (replaces on_event handlers)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    console.print(Panel("[bold green]Starting Dudoxx Extraction API...[/]", border_style="green"))
    
    # Create a table for API info
    api_table = Table(title="API Information", box=ROUNDED)
    api_table.add_column("Property", style="cyan")
    api_table.add_column("Value", style="green")
    
    api_table.add_row("API Title", API_TITLE)
    api_table.add_row("API Version", API_VERSION)
    api_table.add_row("API Documentation", "http://localhost:8000/api/docs")
    api_table.add_row("Progress Updates", "Server-Sent Events (SSE)")
    api_table.add_row("Progress Endpoint", "/api/v1/progress/{request_id}")
    
    console.print(api_table)
    
    console.print(Panel(
        "[bold green]Real-time progress updates are available via Server-Sent Events (SSE).[/]\n"
        "[bold green]Each extraction request returns a unique request_id that can be used to track progress.[/]\n"
        "[bold green]Connect to /api/v1/progress/{request_id} to receive real-time updates.[/]",
        title="Progress Updates Information",
        border_style="green"
    ))
    
    yield
    
    # Shutdown logic
    console.print(Panel("[bold red]Shutting down Dudoxx Extraction API...[/]", border_style="red"))


# Create FastAPI application with lifespan
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        routes=app.routes,
    )
    
    # Add security scheme
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Add security requirement to all operations
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"ApiKeyHeader": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Args:
        request: Request that caused the exception
        exc: Exception that was raised
        
    Returns:
        JSON response with error details
    """
    console.print(Panel("[bold red]Unhandled exception:[/]", border_style="red"))
    console.print_exception()
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "type": exc.__class__.__name__
        }
    )


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    console.print(Panel("[bold]Running Dudoxx Extraction API...[/]", border_style="blue"))
    
    uvicorn.run(
        "dudoxx_extraction_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
