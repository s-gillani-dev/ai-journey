#!/usr/bin/env bash
# Start both the RAG server and Vite dev server.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting NexarAI RAG server on :8000 ..."
cd "$SCRIPT_DIR/rag-server"
uvicorn server:app --port 8000 &
RAG_PID=$!

echo "Starting Vite dev server on :3000 ..."
cd "$SCRIPT_DIR"
npm run dev &
VITE_PID=$!

echo ""
echo "  RAG server  → http://localhost:8000/health"
echo "  App         → http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $RAG_PID $VITE_PID 2>/dev/null; exit 0" INT TERM
wait
