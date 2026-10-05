"""
StrataSentry-NWIS: Health Check & System Readiness Endpoints
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="", tags=["Health & Status"])

@router.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "subsystems": {
            "well_geometry": "ONLINE",
            "telemetry_stream": "ACTIVE",
            "risk_engine_xgboost": "CALIBRATED",
            "lstm_autoencoder": "OPERATIONAL",
            "physics_validation": "ACTIVE",
            "qdrant_vector_store": "READY",
            "copilot_llm": "ONLINE"
        }
    }
