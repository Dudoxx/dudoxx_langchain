#!/usr/bin/env python
"""
Run the Socket.IO server for the Dudoxx Extraction API.

This script runs the Socket.IO server on port 8001.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Socket.IO manager
from dudoxx_extraction_api.socket_manager import run_socketio_server, console

if __name__ == "__main__":
    # Print startup message
    console.print("[bold green]Starting Dudoxx Extraction Socket.IO Server...[/]")
    console.print("[bold]Socket.IO Server:[/] http://localhost:8001")
    
    # Run Socket.IO server
    run_socketio_server(host="0.0.0.0", port=8001)
