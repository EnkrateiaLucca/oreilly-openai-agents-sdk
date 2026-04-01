#!/bin/bash
# Run the Customer Service ChatKit demo
# Requires: conda env 'openai-agents-sdk', Node.js, OPENAI_API_KEY set

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Customer Service Agent (ChatKit)..."
echo "============================================="

# Install frontend deps if needed
if [ ! -d "$DIR/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$DIR/frontend" && npm install
fi

# Start backend (FastAPI)
echo "Starting backend on http://localhost:8000..."
cd "$DIR"
conda run -n openai-agents-sdk --no-banner \
    uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend (Vite)
echo "Starting frontend on http://localhost:5173..."
cd "$DIR/frontend"
npx vite --port 5173 &
FRONTEND_PID=$!

echo ""
echo "Open http://localhost:5173 in your browser"
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to kill both
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
