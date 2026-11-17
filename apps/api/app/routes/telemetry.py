"""
StrataSentry-NWIS: Telemetry Ingestion & Query Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime
from ..schemas.pydantic_models import TelemetryFrameResponse
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/telemetry", tags=["Telemetry"])

@router.get("/{well_id}/latest", response_model=TelemetryFrameResponse)
async def get_latest_telemetry(well_id: str):
    orc = DomainOrchestrator()
    try:
        frame = orc.get_latest_telemetry(well_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown well")
    if not frame:
        raise HTTPException(status_code=404, detail="No active telemetry stream found")
    return frame

@router.get("/{well_id}/history", response_model=List[TelemetryFrameResponse])
async def get_telemetry_history(well_id: str, limit: int = Query(default=50, ge=1, le=120)):
    orc = DomainOrchestrator()
    try:
        return orc.processor_for(well_id).get_recent_history(limit)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown well")

@router.post("/{well_id}/ingest")
async def ingest_frame(well_id: str, frame: TelemetryFrameResponse):
    orc = DomainOrchestrator()
    if frame.well_id != well_id:
        raise HTTPException(status_code=422, detail="Frame well_id must match URL well_id")
    try:
        previous = orc.get_latest_telemetry(well_id)
        if previous:
            prior_time = datetime.fromisoformat(previous["timestamp"].replace("Z", "+00:00"))
            next_time = datetime.fromisoformat(frame.timestamp.replace("Z", "+00:00"))
            if next_time <= prior_time:
                raise HTTPException(status_code=409, detail="Source timestamps must increase; reset synthetic replay before restarting")
        enriched = orc.ingest_telemetry_frame(frame.model_dump())
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown well")
    return {"status": "INGESTED", "measured_depth": enriched.get("measured_depth")}
