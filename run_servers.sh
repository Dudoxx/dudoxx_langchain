#!/bin/bash

# Run the FastAPI server with SSE support

# Source conda to enable conda activate in the script
eval "$(conda shell.bash hook)"

# Activate the conda environment
conda activate dudoxx-langchain

# Install required packages
echo "Installing required packages..."
pip install -r dudoxx_extraction_api/requirements.txt

# Run the FastAPI server
echo "Starting FastAPI server with SSE support..."
python dudoxx_extraction_api/main.py
