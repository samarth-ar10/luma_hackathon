#!/bin/bash
# Script to update the data from the database and start the React web app

echo "===== Updating construction data from database ====="
python upload_demo_data.py

echo "===== Creating public data directory ====="
mkdir -p portia_demo/webui/public/data

echo "===== Copying JSON files to public directory ====="
cp portia_demo/webui/src/data/*.json portia_demo/webui/public/data/
echo "Files copied to public directory"

echo "===== Starting the React web app ====="
cd portia_demo/webui

# Make sure any existing server is stopped
pkill -f "node.*start" || true
sleep 1

# Start the app in development mode
npm start 