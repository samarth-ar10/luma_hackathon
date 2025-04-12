#!/bin/bash
set -e  # Exit on error

echo "===== LUMA Hackathon Web UI Setup ====="

# Check if Python 3.10+ is installed
python3_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python3_version | cut -d. -f1)
python_minor=$(echo $python3_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]); then
    echo "Error: Python 3.10 or higher is required (found $python3_version)"
    exit 1
fi

echo "Python $python3_version found"

# Check if we're in an active virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Using existing virtual environment: $VIRTUAL_ENV"
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -e .[mistral]

echo "===== Setup Complete ====="
echo "To activate the environment: source venv/bin/activate"
echo "To run the test: python 0_simple_test.py"
echo "============================" 