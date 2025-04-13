#!/bin/bash
# Script to restart the Flask server with the new model configuration

echo "===== Killing any existing Flask servers ====="
pkill -f "python.*flask_server/app.py" || echo "No Flask server running"
sleep 1

echo "===== Starting Flask server with new model configuration ====="
cd portia_demo
python flask_server/app.py --port 5003 &
SERVER_PID=$!
echo "Flask server started with PID: $SERVER_PID"
echo "Server is running on http://localhost:5003"

# Wait a moment to see if the server starts successfully
sleep 3
if ps -p $SERVER_PID > /dev/null; then
    echo "Server started successfully. You can now use the AI-powered visualization with the higher context model."
else
    echo "Server failed to start. Please check the logs for errors."
fi 