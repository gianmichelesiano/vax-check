#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
lsof -ti:8510 | xargs kill -9 2>/dev/null || true
sleep 2
source .venv/bin/activate
exec streamlit run src/vaxcheck/ui/app.py --server.port 8510
