#!/bin/bash

# Remove existing directories
rm -rf venv
rm -rf __pycache__

#check if python3.11 is installed
if ! command -v python3.11 &> /dev/null
then
    echo "Python 3.11 could not be found"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    python3.11 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
fi

# Check if directories exist before creating them
mkdir -p tmp
mkdir -p models

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 || { echo "Failed to install torch"; exit 1; }
pip install -r requirements.txt || { echo "Failed to install dependencies"; exit 1; }
