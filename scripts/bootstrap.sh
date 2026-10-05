#!/bin/bash
# ==============================================================================
# STRATASENTRY-NWIS: REPOSITORY BOOTSTRAP SCRIPT
# ==============================================================================

set -e

echo "[*] Initializing StrataSentry-NWIS Environment..."

# Python virtual environment
if [ ! -d "venv" ]; then
    echo "[*] Creating Python virtual environment..."
    python -m venv venv
fi

# Activate venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "[*] Installing Python dependencies..."
pip install --upgrade pip
pip install -r apps/api/requirements.txt

echo "[*] Setting up local service links..."
python scripts/link_services.py

echo "[*] Seeding local datasets..."
python scripts/seed_database.py

echo "[+] Bootstrap complete! Ready to launch stack with 'make run-api' or 'make docker-up'."
