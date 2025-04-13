#!/bin/bash
# Script to copy the JSON data files to the public directory for web access

echo "===== Creating public data directory ====="
mkdir -p portia_demo/webui/public/data

echo "===== Copying JSON files to public directory ====="
cp portia_demo/webui/src/data/*.json portia_demo/webui/public/data/

echo "===== Files copied successfully ====="
ls -la portia_demo/webui/public/data/ 