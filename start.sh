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
EXISTING_PIDS=$(pgrep -f "python.*backend.py" 2>/dev/null || true)

if [ -n "$EXISTING_PIDS" ]; then
    echo "📍 Found existing backend process(es): $EXISTING_PIDS"
    echo "🛑 Stopping existing processes..."
    pkill -9 -f "python.*backend.py" 2>/dev/null || true
    
    # Wait a moment and verify processes are killed
    sleep 2
    REMAINING_PIDS=$(pgrep -f "python.*backend.py" 2>/dev/null || true)
    
    if [ -n "$REMAINING_PIDS" ]; then
        echo "⚠️  Warning: Some processes may still be running: $REMAINING_PIDS"
        echo "   Attempting force kill..."
        kill -9 $REMAINING_PIDS 2>/dev/null || true
        sleep 1
    fi
    
    echo "✅ Previous processes stopped successfully"
else
    echo "✅ No existing processes found"
fi

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
