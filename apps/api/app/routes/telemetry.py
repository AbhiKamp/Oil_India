"""
StrataSentry-NWIS: Telemetry Ingestion & Query Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas.pydantic_models import TelemetryFrameResponse
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/telemetry", tags=["Telemetry"])

@router.get("/{well_id}/latest", response_model=TelemetryFrameResponse)
async def get_latest_telemetry(well_id: str):
    orc = DomainOrchestrator()
    frame = orc.get_latest_telemetry()
    if not frame:
        raise HTTPException(status_code=404, detail="No active telemetry stream found")
    return frame

@router.get("/{well_id}/history", response_model=List[TelemetryFrameResponse])
async def get_telemetry_history(well_id: str, limit: int = 50):
    orc = DomainOrchestrator()
    return orc.stream_processor.get_recent_history(limit)

@router.post("/{well_id}/ingest")
async def ingest_frame(well_id: str, frame: Dict[str, Any]):
    orc = DomainOrchestrator()
    enriched = orc.ingest_telemetry_frame(frame)
    return {"status": "INGESTED", "measured_depth": enriched.get("measured_depth")}
