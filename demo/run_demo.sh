#!/bin/bash
# ==============================================================================
# STRATASENTRY-NWIS: AUTOMATED LIVE DEMO RUNNER
# ==============================================================================

set -e

echo "===================================================================="
echo "  STRATASENTRY-NWIS LIVE DRILLING HAZARD MITIGATION DEMO"
echo "  Well: NHK-421 | Upper Assam Basin | Rig: OIL-RIG-04"
echo "===================================================================="

# 1. Start API Server in background if not already running
echo "[*] Checking FastAPI Gateway status on port 8000..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "[*] Launching API Gateway..."
    uvicorn apps.api.app.main:app --port 8000 &
    API_PID=$!
    sleep 3
else
    echo "[+] API Gateway is already running."
fi

# 2. Launch Telemetry Simulator with Pack-off Hazard Injection
echo "[*] Replaying telemetry with induced pack-off anomaly at 2,845m MD..."
python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff
