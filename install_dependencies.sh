#!/bin/bash

# Install dependencies for the Dudoxx Extraction API

# Source conda to enable conda activate in the script
eval "$(conda shell.bash hook)"

# Activate the conda environment
conda activate dudoxx-langchain

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Install SSE dependency
echo "Installing SSE dependency..."
pip install sse-starlette

# Install PDF processing dependencies
echo "Installing PDF processing dependencies..."
pip install pypdf pypdfium2

# Make the script executable
chmod +x install_dependencies.sh

echo "Dependencies installed successfully!"
