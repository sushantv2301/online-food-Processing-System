#!/usr/bin/env bash
# ==============================================================================
# CineMind NLP - Launch Script
# Engineering Mini Project: Movie Recommendation System using NLP and Python
# Students: Sushant Ingole & Diksha Bhalke
# College: Dr. D. Y. Patil College of Engineering and Innovation (A.Y. 2026-27)
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo "  🎬 CineMind NLP: Movie Recommendation System Web Application"
echo "  Dr. D. Y. Patil College of Engineering and Innovation"
echo "  Students: Sushant Ingole & Diksha Bhalke"
echo "=================================================================="

# Check if virtual environment exists
if [ -d "$DIR/venv" ]; then
    echo "[*] Using project virtual environment..."
    PYTHON_CMD="$DIR/venv/bin/python"
else
    echo "[*] Using system python3..."
    PYTHON_CMD="python3"
fi

# Ensure port 5001 or specified PORT
PORT="${PORT:-5001}"
export PORT

echo "[*] Starting Flask Web Server on http://127.0.0.1:${PORT} ..."
echo "[*] Press Ctrl+C to stop the server at any time."
echo "=================================================================="

"$PYTHON_CMD" app.py
