#!/usr/bin/env python
"""
Socket.IO health check script.

This script checks if the Socket.IO server is running and accessible.
"""

import sys
import time
import argparse
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

# Initialize console for logging
console = Console()

def check_socket_health(url="http://localhost:8001", timeout=5):
    """
    Check if the Socket.IO server is running and accessible.
    
    Args:
        url: Socket.IO server URL
        timeout: Request timeout in seconds
        
    Returns:
        True if the server is running, False otherwise
    """
    try:
        # Try to connect to the Socket.IO server's engine.io endpoint
        response = requests.get(f"{url}/socket.io/?EIO=4&transport=polling", timeout=timeout)
        
        # Check if the response is valid
        if response.status_code == 200 and response.text.startswith("0{"):
            return True, "Socket.IO server is running and accessible"
        else:
            return False, f"Socket.IO server returned unexpected response: {response.status_code} {response.text[:50]}"
    except requests.exceptions.ConnectionError:
        return False, "Socket.IO server is not running or not accessible"
    except requests.exceptions.Timeout:
        return False, "Socket.IO server connection timed out"
    except Exception as e:
        return False, f"Error checking Socket.IO server health: {str(e)}"

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Check Socket.IO server health')
    parser.add_argument('--url', default='http://localhost:8001', help='Socket.IO server URL')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout in seconds')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    args = parser.parse_args()
    
    # Check Socket.IO server health
    is_healthy, message = check_socket_health(args.url, args.timeout)
    
    if args.verbose:
        # Create a rich table for health check info
        health_table = Table(title="Socket.IO Server Health Check", box=ROUNDED)
        health_table.add_column("Property", style="cyan")
        health_table.add_column("Value", style="green" if is_healthy else "red")
        
        health_table.add_row("URL", args.url)
        health_table.add_row("Status", "Healthy" if is_healthy else "Unhealthy")
        health_table.add_row("Message", message)
        
        # Print health check info
        console.print(Panel(health_table, border_style="green" if is_healthy else "red"))
    else:
        # Print simple status message
        if is_healthy:
            console.print(f"[green]Socket.IO server is healthy[/]: {args.url}")
        else:
            console.print(f"[red]Socket.IO server is unhealthy[/]: {args.url} - {message}")
    
    # Return exit code
    return 0 if is_healthy else 1

if __name__ == "__main__":
    sys.exit(main())
