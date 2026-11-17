"""Explicit controls for the local synthetic replay; no connection to rig control."""

import os

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from ..services.orchestrator import DomainOrchestrator
from scripts.simulate_telemetry import frames

router = APIRouter(prefix="/api/v1/demo", tags=["Synthetic Demo"])


def require_demo():
    if os.getenv("ENVIRONMENT", "development").lower() != "development":
        raise HTTPException(status_code=404, detail="Demo controls are disabled outside development")


@router.post("/reset")
async def reset_demo():
    require_demo()
    DomainOrchestrator().stream_processors.clear()
    return {"status": "RESET", "data_source": "synthetic demo data"}


class ReplayRequest(BaseModel):
    scenario: Literal["normal", "packoff", "kick"] = "normal"
    step: int = Field(default=0, ge=0, le=80)
    well_id: Literal["NHK-421"] = "NHK-421"


@router.post("/replay")
async def replay(request: ReplayRequest):
    """Rebuild a short, bounded deterministic window; seeking cannot leak later samples."""
    require_demo()
    orc = DomainOrchestrator()
    processor = orc.processor_for(request.well_id)
    processor.buffer.clear()
    if request.step:
        incident = "none" if request.scenario == "normal" else request.scenario
        for frame in frames(request.well_id, 2.0, incident, request.step):
            orc.ingest_telemetry_frame(frame)
    return {
        "scenario": request.scenario,
        "step": request.step,
        "max_steps": 80,
        "sample_period_seconds": 0.5,
        "telemetry": orc.get_latest_telemetry(request.well_id) or None,
        "risk": orc.evaluate_live_risk(request.well_id) or None,
        "data_source": "deterministic synthetic replay; not connected to eRTMAC",
    }
