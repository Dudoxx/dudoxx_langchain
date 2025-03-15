#!/usr/bin/env python
"""
Test script for Socket.IO server.

This script connects to the Socket.IO server and sends/receives messages
to demonstrate the enhanced logging functionality.
"""

import sys
import time
import uuid
import json
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Initialize console for logging
console = Console()

try:
    import socketio
except ImportError:
    console.print(Panel(
        "[bold red]Error: socketio package not installed[/]\n"
        "Please install it with: [bold]pip install python-socketio[/]",
        title="Dependency Error",
        border_style="red"
    ))
    sys.exit(1)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test Socket.IO server')
parser.add_argument('--url', default='http://localhost:8001', help='Socket.IO server URL')
parser.add_argument('--messages', type=int, default=5, help='Number of test messages to send')
parser.add_argument('--interval', type=float, default=1.0, help='Interval between messages (seconds)')
args = parser.parse_args()

# Create a unique client ID
client_id = str(uuid.uuid4())[:8]

# Create Socket.IO client
sio = socketio.Client(logger=True, engineio_logger=False)

# Event handlers
@sio.event
def connect():
    """Handle connection event."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Create a rich table for connection info
    connection_table = Table(title=f"Connected to Socket.IO Server [{timestamp}]", box=ROUNDED)
    connection_table.add_column("Property", style="cyan")
    connection_table.add_column("Value", style="green")
    
    connection_table.add_row("Server URL", args.url)
    connection_table.add_row("Client ID", client_id)
    connection_table.add_row("Socket ID", sio.sid)
    
    # Print connection info
    console.print(Panel(connection_table, border_style="green"))

@sio.event
def disconnect():
    """Handle disconnection event."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Print disconnection info
    console.print(Panel(
        f"[bold red]Disconnected from Socket.IO server[/]",
        title=f"Disconnection [{timestamp}]",
        border_style="red"
    ))

@sio.event
def connect_error(data):
    """Handle connection error."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Print connection error info
    console.print(Panel(
        f"[bold red]Connection error:[/] {data}",
        title=f"Connection Error [{timestamp}]",
        border_style="red"
    ))

@sio.on('progress')
def on_progress(data):
    """Handle progress event."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Create a rich table for progress info
    progress_table = Table(title=f"Progress Update Received [{timestamp}]", box=ROUNDED)
    progress_table.add_column("Property", style="cyan")
    progress_table.add_column("Value", style="green")
    
    # Add all data fields to the table
    for key, value in data.items():
        progress_table.add_row(key, str(value))
    
    # Print progress info
    console.print(Panel(progress_table, border_style="blue"))

def main():
    """Main function."""
    # Print startup info
    console.print(Panel(
        f"[bold cyan]Socket.IO Test Client[/]\n"
        f"Server URL: [bold]{args.url}[/]\n"
        f"Messages: [bold]{args.messages}[/]\n"
        f"Interval: [bold]{args.interval}[/] seconds",
        title="Test Configuration",
        border_style="cyan"
    ))
    
    try:
        # Connect to Socket.IO server
        console.print("[bold]Connecting to Socket.IO server...[/]")
        sio.connect(args.url)
        
        # Send test messages
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task("[cyan]Sending test messages...", total=args.messages)
            
            for i in range(args.messages):
                # Create test message
                message_id = str(uuid.uuid4())[:8]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # Create a rich table for message info
                message_table = Table(title=f"Test Message {i+1}/{args.messages} [{timestamp}]", box=ROUNDED)
                message_table.add_column("Property", style="cyan")
                message_table.add_column("Value", style="green")
                
                message_table.add_row("Message ID", message_id)
                message_table.add_row("Client ID", client_id)
                message_table.add_row("Socket ID", sio.sid)
                message_table.add_row("Timestamp", timestamp)
                
                # Print message info
                console.print(Panel(message_table, border_style="green"))
                
                # Simulate extraction progress
                percentage = int((i + 1) / args.messages * 100)
                status = "processing"
                if i == 0:
                    status = "starting"
                elif i == args.messages - 1:
                    status = "completed"
                
                # Emit test event
                sio.emit('test_event', {
                    'message_id': message_id,
                    'client_id': client_id,
                    'timestamp': timestamp,
                    'index': i,
                    'total': args.messages
                })
                
                # Wait for interval
                time.sleep(args.interval)
                
                # Update progress
                progress.update(task, advance=1)
        
        # Wait for a moment to receive any final messages
        console.print("[bold]Waiting for final messages...[/]")
        time.sleep(2)
        
        # Disconnect from Socket.IO server
        console.print("[bold]Disconnecting from Socket.IO server...[/]")
        sio.disconnect()
        
        # Print completion info
        console.print(Panel(
            f"[bold green]Test completed successfully[/]\n"
            f"Sent [bold]{args.messages}[/] test messages",
            title="Test Completed",
            border_style="green"
        ))
    
    except Exception as e:
        # Print error info
        console.print(Panel(
            f"[bold red]Error:[/] {str(e)}",
            title="Test Error",
            border_style="red"
        ))
        
        # Print traceback
        import traceback
        console.print(Panel(
            f"[bold red]Traceback:[/]\n{traceback.format_exc()}",
            title="Error Details",
            border_style="red"
        ))
        
        # Ensure disconnection
        if sio.connected:
            sio.disconnect()
        
        # Exit with error
        sys.exit(1)

if __name__ == "__main__":
    main()
