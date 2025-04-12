#!/bin/bash

echo "Starting Flask server for Construction Company Dashboard"
echo "========================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please install python3-venv package."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start the Flask server
echo "Starting Flask server on http://localhost:5000"
python app.py 