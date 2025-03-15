#!/usr/bin/env python
"""
Run the Socket.IO server for the Dudoxx Extraction API.

This script runs the Socket.IO server on port 8001 with enhanced logging
for incoming and outgoing connections and messages.
"""

import os
import sys
import time
import signal
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Socket.IO manager
from dudoxx_extraction_api.socket_manager import (
    run_socketio_server, 
    print_server_status, 
    get_connected_clients_info,
    console
)

# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(sig, frame):
    """Handle SIGINT signal."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    console.print(Panel(
        "[bold yellow]Shutting down Socket.IO server...[/]",
        title=f"Server Shutdown [{timestamp}]",
        border_style="yellow"
    ))
    
    # Print final server status
    print_server_status()
    
    # Exit gracefully
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Create a rich table for startup info
    startup_table = Table(title=f"Dudoxx Extraction Socket.IO Server [{timestamp}]", box=ROUNDED)
    startup_table.add_column("Property", style="cyan")
    startup_table.add_column("Value", style="green")
    
    startup_table.add_row("Server URL", "http://localhost:8001")
    startup_table.add_row("Mode", "Threading")
    startup_table.add_row("CORS", "Enabled (All Origins)")
    startup_table.add_row("Logging", "Enhanced (Rich Console)")
    startup_table.add_row("Client Tracking", "Enabled")
    startup_table.add_row("Message History", "Enabled")
    
    # Print startup info
    console.print(Panel(startup_table, border_style="green"))
    
    # Print usage instructions
    console.print(Panel(
        "[bold cyan]Usage Instructions:[/]\n"
        "- Press [bold]Ctrl+C[/] to shutdown the server\n"
        "- The server will automatically log all connections and messages\n"
        "- Client information is tracked and displayed on connection/disconnection\n"
        "- All progress updates are logged with detailed information",
        title="Socket.IO Server Help",
        border_style="blue"
    ))
    
    # Run Socket.IO server
    try:
        run_socketio_server(host="0.0.0.0", port=8001)
    except Exception as e:
        # Log server error
        console.print(Panel(
            f"[bold red]Failed to start Socket.IO server:[/] {str(e)}",
            title=f"Server Error [{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]",
            border_style="red"
        ))
        
        # Print traceback
        import traceback
        console.print(Panel(
            f"[bold red]Traceback:[/]\n{traceback.format_exc()}",
            title="Error Details",
            border_style="red"
        ))
        
        # Exit with error
        sys.exit(1)
