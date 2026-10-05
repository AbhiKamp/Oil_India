"""
StrataSentry-NWIS: FastAPI Pydantic v2 Models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class WellResponse(BaseModel):
    well_id: str
    well_name: str
    operator: str
    basin: str
    field: str
    status: str
    surface_latitude: float
    surface_longitude: float
    elevation_kb_m: float
    target_depth_md_m: float
    target_formation: str
    current_depth_md: Optional[float] = 2845.5

class TrajectoryStationResponse(BaseModel):
    station_index: int
    measured_depth: float
    inclination_deg: float
    azimuth_deg: float
    true_vertical_depth: float
    northing_delta: float
    easting_delta: float
    dogleg_severity: float
    closure_distance: float

class FormationTopResponse(BaseModel):
    formation_name: str
    md_top: float
    tvd_top: float
    md_bottom: Optional[float] = None
    tvd_bottom: Optional[float] = None
    primary_lithology: str
    hazard_warning: Optional[str] = "NORMAL"

class TelemetryFrameResponse(BaseModel):
    timestamp: str
    well_id: str
    measured_depth: float
    bit_depth: float
    rop: float
    wob: float
    surface_torque: float
    rotary_rpm: int
    standpipe_pressure: float
    flow_in: float
    flow_out_pct: float
    pit_volume: float
    mud_weight_in: float
    ecd: float
    gamma_ray: float
    gas_total: float

class RiskAssessmentResponse(BaseModel):
    alert_id: str
    well_id: str
    timestamp: str
    measured_depth: float
    alert_type: str
    severity: str
    lead_time_seconds: int
    confidence_score: float
    ml_probability: float
    physics_severity: float
    primary_mechanism: str
    driller_action_summary: str
    detailed_sop: List[str]
    historical_citations: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    well_id: str = "NHK-421"
    current_depth: float = 2845.0
    formation: str = "Barail Coal-Shale"
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    engine: str
    evidence_count: int
