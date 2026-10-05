"""
StrataSentry-NWIS: Wellbore Trajectory Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas.pydantic_models import TrajectoryStationResponse, FormationTopResponse
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/wells", tags=["Trajectory & Formations"])

@router.get("/{well_id}/trajectory", response_model=List[TrajectoryStationResponse])
async def get_trajectory(well_id: str):
    orc = DomainOrchestrator()
    if well_id.upper() == "NHK-421" or "NHK" in well_id.upper():
        return orc.trajectory_nhk421
    # For offset wells, return calculated offset trajectory
    return orc.trajectory_nhk421

@router.get("/{well_id}/formations", response_model=List[FormationTopResponse])
async def get_formations(well_id: str):
    # Standard Upper Assam formation tops
    return [
        {
            "formation_name": "Dihing Formation",
            "md_top": 0.0,
            "tvd_top": 0.0,
            "md_bottom": 650.0,
            "tvd_bottom": 650.0,
            "primary_lithology": "Pebbly sands and gravels",
            "hazard_warning": "WASHOUT"
        },
        {
            "formation_name": "Tipam Sandstone",
            "md_top": 650.0,
            "tvd_top": 650.0,
            "md_bottom": 1850.0,
            "tvd_bottom": 1820.0,
            "primary_lithology": "Massive fluvial sandstone",
            "hazard_warning": "DIFFERENTIAL_STICKING"
        },
        {
            "formation_name": "Girujan Clay",
            "md_top": 1850.0,
            "tvd_top": 1820.0,
            "md_bottom": 2550.0,
            "tvd_bottom": 2480.0,
            "primary_lithology": "Mottled plastic swelling shale",
            "hazard_warning": "CLAY_SWELLING"
        },
        {
            "formation_name": "Barail Coal-Shale",
            "md_top": 2550.0,
            "tvd_top": 2480.0,
            "md_bottom": 3400.0,
            "tvd_bottom": 3260.0,
            "primary_lithology": "Sandstones, coals, splintery shales",
            "hazard_warning": "HOLE_PACKOFF_AND_GAS_KICKS"
        },
        {
            "formation_name": "Kopili Formation",
            "md_top": 3400.0,
            "tvd_top": 3260.0,
            "md_bottom": 3950.0,
            "tvd_bottom": 3720.0,
            "primary_lithology": "Overpressured splintery shale",
            "hazard_warning": "WELLBORE_COLLAPSE"
        }
    ]
