#!/bin/bash
# Script to restart the Flask server

echo "===== Killing existing Flask servers ====="
pkill -f "python app.py" || true
echo "Done killing servers"

echo "===== Updating database and exporting data ====="
python upload_demo_data.py

echo "===== Creating public data directory ====="
mkdir -p portia_demo/webui/public/data

echo "===== Copying JSON files to public directory ====="
cp portia_demo/webui/src/data/*.json portia_demo/webui/public/data/
echo "Files copied to public directory"

echo "===== Starting Flask server on port 5002 ====="
python app.py &
SERVER_PID=$!
echo "Flask server started with PID: $SERVER_PID"
echo "Server is running on http://localhost:5002"
echo "Press Ctrl+C to stop"

# Wait for server to be killed
wait $SERVER_PID 