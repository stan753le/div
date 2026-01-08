#!/bin/bash
# Quick start script for SQLite mode

echo "Starting Study Program Recommender System (SQLite mode)"
echo "========================================================="

# Check if database exists
if [ ! -f "backend/data.db" ]; then
    echo ""
    echo "Database not found. Initializing from coursea_data.csv..."
    echo ""
    cd backend
    python3 init_db.py
    cd ..
else
    echo ""
    echo "Database found at backend/data.db"
    echo ""
fi

# Start backend
echo "Starting backend server..."
cd backend
export USE_SQLITE=true
export SQLITE_DB_PATH=data.db
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Backend started (PID: $BACKEND_PID)"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

# Wait for backend to be interrupted
wait $BACKEND_PID
