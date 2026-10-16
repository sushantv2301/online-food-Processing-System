#!/usr/bin/env bash
# ==============================================================================
# FoodQueue Pro - Launch Script
# Engineering Mini Project: Online Food Order Processing System using Queue Data Structure
# Students: Sushant Ingole & Diksha Bhalke
# College: Dr. D. Y. Patil College of Engineering and Innovation (A.Y. 2026-27)
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo "  🍔 FoodQueue Pro: Online Food Order Processing System"
echo "  Topic: First-In-First-Out (FIFO) Queue Data Structure Mini Project"
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

# Launch Flask Application
echo "[*] Launching Web Application..."
echo "[*] Features Active:"
echo "    - Customer Menu & Real-Time Order Placement (Enqueue O(1))"
echo "    - Live Order Status Tracking & Queue Position Countdown"
echo "    - McDonald's Style Split-Screen Pickup Counter Display"
echo "    - Kitchen Display System (KDS) with Strict FIFO Dequeue (O(1))"
echo "    - Dynamic Queue DSA Memory Visualizer & Viva Reference Guide"
echo "=================================================================="
echo "[*] Press Ctrl+C to terminate the server."

"$PYTHON_CMD" app.py
