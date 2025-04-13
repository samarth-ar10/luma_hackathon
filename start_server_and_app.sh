#!/bin/bash
# Start both the Flask server and React web UI

echo "===== Starting Flask Server with Worker AI Integration ====="
# Start the Flask server in the background
python app.py &
FLASK_PID=$!

# Give the server a moment to start
sleep 3

echo "===== Flask server started with PID: $FLASK_PID ====="

echo "===== Starting React Web UI ====="
# Run the existing start_webui script
./start_webui.sh

# When the web UI is closed, also kill the Flask server
kill $FLASK_PID