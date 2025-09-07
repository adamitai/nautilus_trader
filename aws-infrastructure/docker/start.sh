#!/bin/bash

# Start script for Nautilus Trader Arbitrage Tools
# This script starts both the backend API and nginx reverse proxy

set -e

echo "Starting Nautilus Trader Arbitrage Tools..."

# Start the backend API server in the background
echo "Starting backend API server..."
python arbitrage_tools/api_server.py &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 2

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "ERROR: Backend API server failed to start"
    exit 1
fi

echo "Backend API server started (PID: $BACKEND_PID)"

# Start nginx
echo "Starting nginx reverse proxy..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Wait a moment for nginx to start
sleep 2

# Check if nginx is running
if ! kill -0 $NGINX_PID 2>/dev/null; then
    echo "ERROR: Nginx failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "Nginx reverse proxy started (PID: $NGINX_PID)"
echo "Application is ready!"

# Function to handle shutdown
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $NGINX_PID 2>/dev/null || true
    wait
    echo "Shutdown complete"
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for processes
wait $BACKEND_PID $NGINX_PID
