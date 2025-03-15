"""
Progress manager for the Dudoxx Extraction API.

This module provides Server-Sent Events (SSE) functionality for real-time progress updates.
"""

from typing import Dict, Any, Optional, List
import asyncio
import uuid
import time
import json
from collections import defaultdict
from fastapi import Request
from sse_starlette.sse import EventSourceResponse
from rich.console import Console
from rich.panel import Panel

# Initialize console for logging
console = Console()

# Store progress updates by request ID
progress_updates = defaultdict(list)
active_connections = {}

async def event_generator(request: Request, request_id: str):
    """
    Generate SSE events for a specific request ID.
    
    Args:
        request: FastAPI request object
        request_id: Unique identifier for the request
        
    Yields:
        SSE events
    """
    client_id = str(uuid.uuid4())
    active_connections[client_id] = request_id
    
    console.print(Panel(
        f"[bold green]Client {client_id} connected to progress stream for request {request_id}[/]",
        title="SSE Connection Established",
        border_style="green"
    ))
    
    # Send any existing progress updates for this request
    if request_id in progress_updates and progress_updates[request_id]:
        for update in progress_updates[request_id]:
            yield {
                "event": "progress",
                "data": json.dumps(update)  # Ensure data is properly JSON-encoded
            }
            # Add a small delay between sending existing updates to prevent them from arriving all at once
            await asyncio.sleep(0.1)
    else:
        # Send initial status if no updates exist
        initial_update = {
            "status": "starting",
            "message": "Connected to progress stream",
            "timestamp": time.time()
        }
        yield {
            "event": "progress",
            "data": json.dumps(initial_update)  # Ensure data is properly JSON-encoded
        }
    
    try:
        while True:
            if await request.is_disconnected():
                break
                
            # Check for new updates every 100ms
            await asyncio.sleep(0.1)
            
            # Send any new updates that have been added since last check
            if request_id in progress_updates and progress_updates[request_id]:
                update = progress_updates[request_id].pop(0)
                yield {
                    "event": "progress",
                    "data": json.dumps(update)  # Ensure data is properly JSON-encoded
                }
                
                # Add a small delay after sending an update to ensure they don't arrive all at once
                await asyncio.sleep(0.05)
    finally:
        # Clean up when client disconnects
        if client_id in active_connections:
            del active_connections[client_id]
            console.print(f"[yellow]Client {client_id} disconnected from progress stream[/]")

def add_progress_update(request_id: str, status: str, message: str, percentage: Optional[int] = None):
    """
    Add a progress update for a specific request ID.
    
    Args:
        request_id: Unique identifier for the request
        status: Status of the extraction ('starting', 'processing', 'completed', 'error')
        message: Progress message
        percentage: Optional percentage of completion (0-100)
    """
    update = {
        "status": status,
        "message": message,
        "timestamp": time.time()
    }
    
    if percentage is not None:
        update["percentage"] = percentage
    
    # Convert to JSON string for logging
    update_str = json.dumps(update)
    
    console.print(f"[blue]Progress update for request {request_id}:[/] {update_str}")
    
    progress_updates[request_id].append(update)
    
    # Clean up old updates to prevent memory leaks
    # Keep only the last 100 updates per request
    if len(progress_updates[request_id]) > 100:
        progress_updates[request_id] = progress_updates[request_id][-100:]
    
    # Remove request IDs that haven't been accessed in a while
    current_time = time.time()
    for req_id in list(progress_updates.keys()):
        if not progress_updates[req_id]:
            del progress_updates[req_id]

def get_progress_endpoint(request: Request, request_id: str):
    """
    SSE endpoint for progress updates.
    
    Args:
        request: FastAPI request object
        request_id: Unique identifier for the request
        
    Returns:
        EventSourceResponse for SSE
    """
    return EventSourceResponse(event_generator(request, request_id))

def get_active_connections_count():
    """
    Get the number of active SSE connections.
    
    Returns:
        Number of active connections
    """
    return len(active_connections)

def get_active_requests_count():
    """
    Get the number of active requests with progress updates.
    
    Returns:
        Number of active requests
    """
    return len(progress_updates)


def get_progress_callback():
    """
    Get a callback function for progress updates.
    
    Returns:
        Callback function that takes request_id, status, message, and percentage
    """
    def progress_callback(request_id: str, status: str, message: str, percentage: Optional[int] = None):
        add_progress_update(request_id, status, message, percentage)
    
    return progress_callback
