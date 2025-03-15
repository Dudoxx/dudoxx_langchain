"""
Socket.IO manager for the Dudoxx Extraction API.

This module provides Socket.IO functionality for real-time progress updates.
"""

# Apply eventlet monkey patching before importing any other modules
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
from typing import Dict, Any, Optional
from rich.console import Console

# Initialize console for logging
console = Console()

# Create Flask app
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'dudoxx-extraction-secret'

# Create Socket.IO instance - renamed to sio to match what main.py expects
sio = SocketIO(
    flask_app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)


@sio.on('connect')
def handle_connect():
    """
    Handle client connection.
    """
    console.print(f"[bold green]Client connected[/]")


@sio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    console.print(f"[bold red]Client disconnected[/]")


def emit_progress(status: str, message: str, percentage: Optional[int] = None):
    """
    Emit progress update to all connected clients.
    
    Args:
        status: Status of the extraction ('starting', 'processing', 'completed', 'error')
        message: Progress message
        percentage: Optional percentage of completion (0-100)
    """
    data = {
        'status': status,
        'message': message
    }
    
    if percentage is not None:
        data['percentage'] = percentage
    
    sio.emit('progress', data)
    console.print(f"[bold blue]Progress update:[/] {status} - {message}")


# Extraction progress tracking
def track_extraction_progress(operation_id: str, status: str, message: str, percentage: Optional[int] = None):
    """
    Track extraction progress and emit updates.
    
    Args:
        operation_id: Unique identifier for the extraction operation
        status: Status of the extraction ('starting', 'processing', 'completed', 'error')
        message: Progress message
        percentage: Optional percentage of completion (0-100)
    """
    emit_progress(status, message, percentage)


# Run the Socket.IO server
def run_socketio_server(host='0.0.0.0', port=8001):
    """
    Run the Socket.IO server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    sio.run(flask_app, host=host, port=port)
