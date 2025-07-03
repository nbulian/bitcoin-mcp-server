#!/bin/bash
# Production startup script for Bitcoin MCP Server

echo "Starting Bitcoin MCP Server..."

# Set default port if not provided
export PORT=${PORT:-8000}

# Start the server
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1 