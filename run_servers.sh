#!/bin/bash

# Run the FastAPI server and Socket.IO server in separate processes

# Source conda to enable conda activate in the script
eval "$(conda shell.bash hook)"

# Activate the conda environment
conda activate dudoxx-langchain

# Install required packages
echo "Installing required packages..."
pip install -r dudoxx_extraction_api/requirements.txt

# Run the Socket.IO server in the background
echo "Starting Socket.IO server..."
python dudoxx_extraction_api/run_socketio.py &
SOCKETIO_PID=$!

# Wait a moment for the Socket.IO server to start
sleep 2

# Run the FastAPI server
echo "Starting FastAPI server..."
python dudoxx_extraction_api/main.py

# When the FastAPI server is stopped, also stop the Socket.IO server
echo "Stopping Socket.IO server..."
kill $SOCKETIO_PID
