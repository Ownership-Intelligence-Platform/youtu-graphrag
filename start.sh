#!/bin/bash

echo "🌟 Starting Youtu-GraphRAG Server..."
echo "=========================================="

git pull

# Check if required files exist
if [ ! -f "backend.py" ]; then
    echo "❌ backend.py not found. Please run this script from the project root directory."
    exit 1
fi

if [ ! -f "frontend/index.html" ]; then
    echo "❌ frontend/index.html not found."
    exit 1
fi

# Kill any existing backend processes
echo "🔄 Checking for existing processes..."
pkill -f backend.py 2>/dev/null || true

# Start the backend server
echo "🚀 Starting backend server in background..."
echo "=========================================="

nohup python backend.py > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend server started (PID: $BACKEND_PID)"
echo "� Logs are being written to ../backend.log"
echo "🌐 Server should be available at http://localhost:8003"
echo ""
echo "To stop the server, run: kill $BACKEND_PID"
echo "Or to stop all backend processes: pkill -f backend.py"
