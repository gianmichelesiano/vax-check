#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Kill existing processes on our ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 0.5

cleanup() {
  echo ""
  echo "=== Shutting down ==="
  kill $API_PID 2>/dev/null || true
  wait $API_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

source .venv/bin/activate

echo "┌──────────────────────────────────────────────┐"
echo "│  API  → http://localhost:8000               │"
echo "│  FE   → http://localhost:3000               │"
echo "│  Ctrl+C to stop both                        │"
echo "└──────────────────────────────────────────────┘"
echo ""

uvicorn vaxcheck.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

cd frontend
npm run dev

cleanup
