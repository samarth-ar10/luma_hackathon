#!/bin/bash
# Script to start the React app

echo "===== Stopping any running React servers ====="
pkill -f "node.*start" || true
sleep 1

echo "===== Starting React app ====="
cd portia_demo/webui

echo "===== Running npm start ====="
npm start 