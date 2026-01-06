#!/bin/bash

# Render Deployment Startup Script
# This script starts both Backend and LightRAG services

set -e

echo "============================================"
echo "  Starting Farm Vaidya Services on Render"
echo "============================================"

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if .env exists (though Render uses environment variables)
if [ -f .env ]; then
    echo "Loading .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Start LightRAG Server in background
echo "Starting LightRAG Server on port ${LIGHTRAG_PORT:-9621}..."
cd lightrag/Lightrag_main

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "ERROR: LightRAG virtual environment not found!"
    echo "Run: uv sync --extra api"
    exit 1
fi

# Activate and start LightRAG
source .venv/bin/activate
nohup lightrag-server > lightrag.log 2>&1 &
LIGHTRAG_PID=$!
echo "LightRAG started with PID: $LIGHTRAG_PID"

# Wait for LightRAG to be ready
sleep 5

# Go back to backend
cd ../..

# Start Backend Server in foreground
echo "Starting Backend Server on port ${PORT:-8000}..."

# Check if backend venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Backend virtual environment not found!"
    echo "Run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Activate and start backend (in foreground for Render)
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
