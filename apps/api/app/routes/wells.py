"""
StrataSentry-NWIS: Wells REST Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.pydantic_models import WellResponse
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/wells", tags=["Wells"])

@router.get("", response_model=List[WellResponse])
async def list_wells():
    orc = DomainOrchestrator()
    return orc.wells

@router.get("/{well_id}", response_model=WellResponse)
async def get_well(well_id: str):
    orc = DomainOrchestrator()
    for w in orc.wells:
        if w["well_id"] == well_id or w["well_name"] == well_id:
            return w
    raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
