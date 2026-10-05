#!/bin/bash
# ==============================================================================
# STRATASENTRY-NWIS: LOCAL STACK LAUNCHER
# ==============================================================================

set -e

echo "[*] Launching StrataSentry FastAPI Gateway on port 8000..."
uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo "[*] Launching Next.js Tactical HUD on port 3000..."
cd apps/dashboard
npm run dev &
UI_PID=$!
cd ../..

echo "[+] Stack active! Press CTRL+C to terminate all services."
trap "kill $API_PID $UI_PID" EXIT
wait
