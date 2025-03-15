    #!/usr/bin/env python
"""
Test script for Socket.IO server.

This script sends a test message to the Socket.IO server.
"""

import socketio
import time

# Create Socket.IO client
sio = socketio.Client()

# Define event handlers
@sio.event
def connect():
    print("Connected to Socket.IO server!")

@sio.event
def disconnect():
    print("Disconnected from Socket.IO server!")

@sio.on('progress')
def on_progress(data):
    print(f"Progress update: {data}")

# Connect to Socket.IO server
try:
    print("Connecting to Socket.IO server...")
    sio.connect('http://localhost:8001')
    
    # Wait for a moment to receive any messages
    print("Waiting for messages...")
    time.sleep(5)
    
    # Disconnect
    sio.disconnect()
except Exception as e:
    print(f"Error: {e}")
