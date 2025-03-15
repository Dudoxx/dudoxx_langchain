"""
Socket.IO manager for the Dudoxx Extraction API.

This module provides Socket.IO functionality for real-time progress updates.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Set
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from rich.style import Style

# Initialize console for logging
console = Console()

# Flag to track if Socket.IO is available
socket_io_available = False
sio = None
flask_app = None

# Track connected clients and their session info
connected_clients: Dict[str, Dict[str, Any]] = {}
message_history: Dict[str, Dict[str, Any]] = {}

# Try to initialize Socket.IO, but don't fail if dependencies are missing
try:
    import eventlet
    from flask import Flask, request
    from flask_socketio import SocketIO
    
    # Create Flask app
    flask_app = Flask(__name__)
    flask_app.config['SECRET_KEY'] = 'dudoxx-extraction-secret'
    
    # Create Socket.IO instance
    sio = SocketIO(
        flask_app,
        cors_allowed_origins="*",
        async_mode="threading",  # Use threading instead of eventlet to avoid monkey patching
        logger=True,
        engineio_logger=True
    )
    
    socket_io_available = True
    
    @sio.on('connect')
    def handle_connect():
        """
        Handle client connection.
        """
        client_id = request.sid
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Store client information
        connected_clients[client_id] = {
            'connected_at': timestamp,
            'ip': request.remote_addr or 'unknown',
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'transport': request.headers.get('Upgrade', 'polling'),
            'messages_received': 0,
            'messages_sent': 0,
            'last_activity': timestamp
        }
        
        # Create a rich table for client info
        client_table = Table(title=f"Client Connected [{timestamp}]", box=ROUNDED, style="green")
        client_table.add_column("Property", style="cyan")
        client_table.add_column("Value", style="green")
        
        client_table.add_row("Client ID", client_id)
        client_table.add_row("IP Address", connected_clients[client_id]['ip'])
        client_table.add_row("User Agent", connected_clients[client_id]['user_agent'])
        client_table.add_row("Transport", connected_clients[client_id]['transport'])
        
        # Print client connection info
        console.print(Panel(client_table, border_style="green"))
        
        # Log total connected clients
        console.print(f"[bold green]Total connected clients:[/] {len(connected_clients)}")
    
    @sio.on('disconnect')
    def handle_disconnect():
        """
        Handle client disconnection.
        """
        client_id = request.sid
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if client_id in connected_clients:
            # Calculate connection duration
            connected_at = connected_clients[client_id]['connected_at']
            
            # Create a rich table for client info
            client_table = Table(title=f"Client Disconnected [{timestamp}]", box=ROUNDED, style="red")
            client_table.add_column("Property", style="cyan")
            client_table.add_column("Value", style="red")
            
            client_table.add_row("Client ID", client_id)
            client_table.add_row("IP Address", connected_clients[client_id]['ip'])
            client_table.add_row("Connected At", connected_at)
            client_table.add_row("Messages Received", str(connected_clients[client_id]['messages_received']))
            client_table.add_row("Messages Sent", str(connected_clients[client_id]['messages_sent']))
            
            # Remove client from connected clients
            del connected_clients[client_id]
            
            # Print client disconnection info
            console.print(Panel(client_table, border_style="red"))
            
            # Log total connected clients
            console.print(f"[bold red]Total connected clients:[/] {len(connected_clients)}")
        else:
            console.print(f"[bold red]Unknown client disconnected:[/] {client_id}")
    
    @sio.on_error()
    def handle_error(e):
        """
        Handle Socket.IO errors.
        """
        client_id = request.sid if hasattr(request, 'sid') else 'unknown'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Print error info
        console.print(Panel(
            f"[bold red]Socket.IO Error:[/]\nClient: {client_id}\nError: {str(e)}",
            title=f"Socket.IO Error [{timestamp}]",
            border_style="red"
        ))
    
    @sio.on('*')
    def catch_all(event, data):
        """
        Catch all events for logging.
        """
        client_id = request.sid
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if client_id in connected_clients:
            connected_clients[client_id]['messages_received'] += 1
            connected_clients[client_id]['last_activity'] = timestamp
        
        # Log the event
        console.print(Panel(
            f"[bold cyan]Event:[/] {event}\n[bold cyan]Data:[/] {data}",
            title=f"Received Event from {client_id} [{timestamp}]",
            border_style="cyan"
        ))
    
except ImportError as e:
    console.print(Panel(
        f"[yellow]Socket.IO dependencies not available: {e}[/]\n"
        f"[yellow]Progress updates will be logged but not emitted to clients[/]",
        title="Socket.IO Initialization Error",
        border_style="yellow"
    ))


def emit_progress(status: str, message: str, percentage: Optional[int] = None, room: Optional[str] = None):
    """
    Emit progress update to all connected clients or a specific room.
    
    Args:
        status: Status of the extraction ('starting', 'processing', 'completed', 'error')
        message: Progress message
        percentage: Optional percentage of completion (0-100)
        room: Optional room to emit to (client ID)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    message_id = str(uuid.uuid4())[:8]
    
    data = {
        'status': status,
        'message': message,
        'timestamp': timestamp,
        'message_id': message_id
    }
    
    if percentage is not None:
        data['percentage'] = percentage
    
    # Store message in history
    message_history[message_id] = {
        'data': data,
        'timestamp': timestamp,
        'room': room,
        'delivered': False
    }
    
    # Only emit if Socket.IO is available
    if socket_io_available and sio is not None:
        try:
            # Create a rich table for message info
            message_table = Table(title=f"Emitting Progress Update [{timestamp}]", box=ROUNDED)
            message_table.add_column("Property", style="cyan")
            message_table.add_column("Value", style="green")
            
            message_table.add_row("Message ID", message_id)
            message_table.add_row("Status", status)
            message_table.add_row("Message", message)
            if percentage is not None:
                message_table.add_row("Percentage", f"{percentage}%")
            message_table.add_row("Room", room or "broadcast")
            
            # Print message info
            console.print(Panel(message_table, border_style="green"))
            
            # Emit the message
            if room:
                sio.emit('progress', data, room=room)
                if room in connected_clients:
                    connected_clients[room]['messages_sent'] += 1
            else:
                sio.emit('progress', data)
                # Update message count for all connected clients
                for client_id in connected_clients:
                    connected_clients[client_id]['messages_sent'] += 1
            
            # Mark message as delivered
            message_history[message_id]['delivered'] = True
            
            # Log success
            console.print(f"[bold green]Progress update emitted successfully[/] (ID: {message_id})")
        except Exception as e:
            # Log error
            console.print(Panel(
                f"[bold red]Failed to emit progress update:[/] {e}",
                title=f"Emission Error [{timestamp}]",
                border_style="red"
            ))
    else:
        # Log progress update even if Socket.IO is not available
        status_style = {
            'starting': 'blue',
            'processing': 'yellow',
            'completed': 'green',
            'error': 'red'
        }.get(status, 'white')
        
        console.print(Panel(
            f"[bold {status_style}]Status:[/] {status}\n"
            f"[bold {status_style}]Message:[/] {message}\n"
            + (f"[bold {status_style}]Percentage:[/] {percentage}%" if percentage is not None else ""),
            title=f"Progress Update [{timestamp}] (Socket.IO not available)",
            border_style=status_style
        ))


# Extraction progress tracking with operation ID
def track_extraction_progress(operation_id: str, status: str, message: str, percentage: Optional[int] = None):
    """
    Track extraction progress and emit updates.
    
    Args:
        operation_id: Unique identifier for the extraction operation
        status: Status of the extraction ('starting', 'processing', 'completed', 'error')
        message: Progress message
        percentage: Optional percentage of completion (0-100)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Create a rich table for operation info
    operation_table = Table(title=f"Operation Progress [{timestamp}]", box=ROUNDED)
    operation_table.add_column("Property", style="cyan")
    operation_table.add_column("Value", style="green")
    
    operation_table.add_row("Operation ID", operation_id)
    operation_table.add_row("Status", status)
    operation_table.add_row("Message", message)
    if percentage is not None:
        operation_table.add_row("Percentage", f"{percentage}%")
    
    # Print operation info
    console.print(Panel(operation_table, border_style="blue"))
    
    # Emit progress update
    emit_progress(status, message, percentage)


# Get connected clients info
def get_connected_clients_info():
    """
    Get information about connected clients.
    
    Returns:
        Dict with client information
    """
    return connected_clients


# Print server status
def print_server_status():
    """
    Print the current server status.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Create a rich table for server info
    server_table = Table(title=f"Socket.IO Server Status [{timestamp}]", box=ROUNDED)
    server_table.add_column("Property", style="cyan")
    server_table.add_column("Value", style="green")
    
    server_table.add_row("Available", "Yes" if socket_io_available else "No")
    server_table.add_row("Connected Clients", str(len(connected_clients)))
    server_table.add_row("Messages in History", str(len(message_history)))
    
    # Print server info
    console.print(Panel(server_table, border_style="blue"))
    
    # Print connected clients if any
    if connected_clients:
        clients_table = Table(title="Connected Clients", box=ROUNDED)
        clients_table.add_column("Client ID", style="cyan")
        clients_table.add_column("IP Address", style="green")
        clients_table.add_column("Connected At", style="green")
        clients_table.add_column("Messages Received", style="green")
        clients_table.add_column("Messages Sent", style="green")
        
        for client_id, client_info in connected_clients.items():
            clients_table.add_row(
                client_id,
                client_info['ip'],
                client_info['connected_at'],
                str(client_info['messages_received']),
                str(client_info['messages_sent'])
            )
        
        console.print(clients_table)


# Run the Socket.IO server
def run_socketio_server(host='0.0.0.0', port=8001):
    """
    Run the Socket.IO server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    if socket_io_available and sio is not None and flask_app is not None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Print server startup info
        server_table = Table(title=f"Socket.IO Server Starting [{timestamp}]", box=ROUNDED)
        server_table.add_column("Property", style="cyan")
        server_table.add_column("Value", style="green")
        
        server_table.add_row("Host", host)
        server_table.add_row("Port", str(port))
        server_table.add_row("Mode", "Threading")
        server_table.add_row("CORS", "Enabled (All Origins)")
        
        console.print(Panel(server_table, border_style="green"))
        
        try:
            # Run the server
            sio.run(flask_app, host=host, port=port)
        except Exception as e:
            # Log server error
            console.print(Panel(
                f"[bold red]Failed to start Socket.IO server:[/] {e}",
                title=f"Server Error [{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]",
                border_style="red"
            ))
    else:
        # Log server unavailable
        console.print(Panel(
            "[bold red]Socket.IO server cannot be started: dependencies not available[/]",
            title=f"Server Error [{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]",
            border_style="red"
        ))
