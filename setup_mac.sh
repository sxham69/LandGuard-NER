#!/bin/zsh
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "🚨 LandslideGuard NER • Mac Setup"
echo "--------------------------------"

PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python)"
else
  echo "❌ Python 3 was not found."
  echo "Install Python 3 and run this script again."
  exit 1
fi

if [ ! -d "$ROOT_DIR/.venv" ]; then
  echo "▶ Creating virtual environment..."
  "$PYTHON_CMD" -m venv "$ROOT_DIR/.venv"
fi

PYTHON="$ROOT_DIR/.venv/bin/python3"
[ -x "$PYTHON" ] || PYTHON="$ROOT_DIR/.venv/bin/python"

echo "▶ Bootstrapping pip..."
"$PYTHON" -m ensurepip --upgrade >/dev/null 2>&1 || true

echo "▶ Installing dependencies..."
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt"

chmod +x "$ROOT_DIR/run.sh" "$ROOT_DIR/setup_mac.sh"

echo ""
echo "✅ Setup complete."
echo "Run the application with:"
echo "   ./run.sh"
echo ""
echo "Dashboard: http://localhost:8501"
echo "API:       http://localhost:8000"
