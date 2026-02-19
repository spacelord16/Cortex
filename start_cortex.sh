#!/bin/bash

# Kill ports 8000 and 3000 just in case
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "--- Starting Cortex Backend (FastAPI) ---"
# Check if uv is installed
if command -v uv &> /dev/null; then
    uv run uvicorn app.main:app --reload --port 8000 &
else
    echo "uv not found, using python3"
    python3 -m uvicorn app.main:app --reload --port 8000 &
fi

PID_BACKEND=$!
echo "Backend running on PID $PID_BACKEND"

echo "--- Starting Cortex Frontend (Next.js) ---"
cd frontend
npm run dev &
PID_FRONTEND=$!
cd ..

echo "Frontend running on PID $PID_FRONTEND"
echo "Access Cortex at http://localhost:3000"
echo "Press CTRL+C to stop both servers"

wait
