"""
Main application for the Dudoxx Extraction API.

This module initializes the FastAPI application and includes the API routes.
"""

import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from rich.console import Console

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Dudoxx Extraction components
from dudoxx_extraction.domains.domain_init import initialize_domains

# Import API components
from dudoxx_extraction_api.config import API_TITLE, API_DESCRIPTION, API_VERSION
from dudoxx_extraction_api.routes import router

# Initialize console for logging
console = Console()

# Initialize domains
initialize_domains()

# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
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


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    console.print("[bold green]Starting Dudoxx Extraction API...[/]")
    console.print(f"[bold]API Title:[/] {API_TITLE}")
    console.print(f"[bold]API Version:[/] {API_VERSION}")
    console.print(f"[bold]API Documentation:[/] http://localhost:8000/api/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    """
    console.print("[bold red]Shutting down Dudoxx Extraction API...[/]")


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
    console.print("[bold red]Unhandled exception:[/]")
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
    
    console.print("[bold]Running Dudoxx Extraction API...[/]")
    uvicorn.run(
        "dudoxx_extraction_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
