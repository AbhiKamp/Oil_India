"""
StrataSentry-NWIS: Wellbore Trajectory Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas.pydantic_models import TrajectoryStationResponse, FormationTopResponse
from ..services.orchestrator import DomainOrchestrator
from ..services.report_data import formations as report_formations

router = APIRouter(prefix="/api/v1/wells", tags=["Trajectory & Formations"])

@router.get("/{well_id}/trajectory", response_model=List[TrajectoryStationResponse])
async def get_trajectory(well_id: str):
    orc = DomainOrchestrator()
    well = next((w for w in orc.wells if w["well_id"].casefold() == well_id.casefold()), None)
    if well is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
    return orc.trajectory_nhk421 if well["well_id"] == "NHK-421" else []

@router.get("/{well_id}/formations", response_model=List[FormationTopResponse])
async def get_formations(well_id: str):
    orc = DomainOrchestrator()
    well = next((w for w in orc.wells if w["well_id"].casefold() == well_id.casefold()), None)
    if well is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
    result = report_formations(well_id)
    return result if result is not None else []
