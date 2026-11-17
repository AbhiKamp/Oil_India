"""
StrataSentry-NWIS: Health Check & System Readiness Endpoints
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from shutil import which
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="", tags=["Health & Status"])

@router.get("/health")
async def health_check():
    orc = DomainOrchestrator()
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.2.0-local-prototype",
        "subsystems": {
            "well_geometry": f"{len(orc.trajectory_nhk421)} supplied synthetic survey stations",
            "telemetry_stream": "synthetic samples present" if any(p.buffer for p in orc.stream_processors.values()) else "no samples; replay not started",
            "risk_engine": "uncalibrated heuristic; not a trained XGBoost/LSTM model",
            "experimental_classifier": "isolated synthetic-data experiment; not enabled for alerts",
            "retrieval": "local lexical search; no remote vector database",
            "copilot": "evidence-only extractive summary; no language model",
            "ocr_tools": "installed" if which("tesseract") and which("pdftoppm") else "unavailable",
            "ertmac": "not connected",
        },
        "scope": "Process liveness and configured local modes, not operational certification.",
    }
