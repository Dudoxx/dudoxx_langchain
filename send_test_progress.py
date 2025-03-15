#!/usr/bin/env python
"""
Send a test progress update to the Socket.IO server.

This script sends a test progress update to the Socket.IO server.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Socket.IO manager
from dudoxx_extraction_api.socket_manager import track_extraction_progress

# Send a test progress update
track_extraction_progress(
    operation_id="test-operation",
    status="processing",
    message="This is a test progress update",
    percentage=50
)

print("Test progress update sent!")
