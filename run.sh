#!/bin/zsh
set -u
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"
PYTHON="$ROOT_DIR/.venv/bin/python3"
[ -x "$PYTHON" ] || PYTHON="$ROOT_DIR/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then echo "❌ Virtual environment Python not found. Run ./setup_mac.sh"; exit 1; fi

echo "🚨 LandslideGuard NER • State EOC"
echo "--------------------------------"
"$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt"

API_LOG="$ROOT_DIR/api.log"
cleanup() {
  echo ""
  echo "Stopping LandslideGuard services..."
  [ -n "${API_PID:-}" ] && kill "$API_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "▶ Starting FastAPI on http://127.0.0.1:8000"
"$PYTHON" -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 >"$API_LOG" 2>&1 &
API_PID=$!

READY=0
for i in {1..20}; do
  if ! kill -0 "$API_PID" 2>/dev/null; then
    echo "❌ FastAPI stopped unexpectedly."
    echo "--- backend error ---"
    cat "$API_LOG"
    exit 1
  fi
  if "$PYTHON" -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1)' >/dev/null 2>&1; then READY=1; break; fi
  sleep 0.5
done
if [ "$READY" -ne 1 ]; then
  echo "❌ FastAPI did not become ready."
  echo "--- backend error ---"
  cat "$API_LOG"
  exit 1
fi
echo "✅ FastAPI online"

echo "▶ Starting Streamlit on http://localhost:8501"
"$PYTHON" -m streamlit run "$ROOT_DIR/frontend/app.py" --server.address 127.0.0.1 --server.port 8501
