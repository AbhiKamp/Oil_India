"""
StrataSentry-NWIS: Real-Time Risk & Hazard Alerts Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..schemas.pydantic_models import RiskAssessmentResponse
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/risks", tags=["Risk & Hazards"])

@router.get("/{well_id}/current", response_model=RiskAssessmentResponse)
async def get_current_risk(well_id: str):
    orc = DomainOrchestrator()
    try:
        alert = orc.evaluate_live_risk(well_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown well")
    if not alert:
        raise HTTPException(status_code=404, detail="Risk evaluation unavailable")
    return alert

@router.get("/{well_id}/alerts", response_model=List[RiskAssessmentResponse])
async def list_alerts(well_id: str):
    orc = DomainOrchestrator()
    try:
        alert = orc.evaluate_live_risk(well_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown well")
    return [alert] if alert else []
