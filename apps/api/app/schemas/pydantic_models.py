"""
StrataSentry-NWIS: FastAPI Pydantic v2 Models
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
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
    current_depth_md: Optional[float] = None

class NearbyWellResponse(BaseModel):
    well_id: str
    well_name: str
    field: str
    surface_latitude: float
    surface_longitude: float
    distance_km: float

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
    tvd_top: Optional[float] = None
    md_bottom: Optional[float] = None
    tvd_bottom: Optional[float] = None
    primary_lithology: Optional[str] = None
    hazard_warning: Optional[str] = None
    depth_reference: str = "MD"
    datum: Optional[str] = None
    method: str
    source_file: str
    source_section: str

class TelemetryFrameResponse(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    timestamp: str = Field(max_length=64)
    well_id: str
    measured_depth: float = Field(ge=0)
    bit_depth: float = Field(ge=0)
    rop: float = Field(ge=0)
    wob: float = Field(ge=0)
    surface_torque: float = Field(ge=0)
    rotary_rpm: int = Field(ge=0)
    standpipe_pressure: float = Field(ge=0)
    flow_in: float = Field(ge=0)
    flow_out_pct: float = Field(ge=0)
    pit_volume: float = Field(ge=0)
    mud_weight_in: float = Field(gt=0)
    ecd: float = Field(gt=0)
    gamma_ray: float = Field(ge=0)
    gas_total: float = Field(ge=0)

    @field_validator("timestamp")
    @classmethod
    def timestamp_is_aware(cls, value: str) -> str:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include a time zone")
        return value

    @field_validator("measured_depth", "bit_depth", "rop", "wob", "surface_torque",
                     "standpipe_pressure", "flow_in", "flow_out_pct", "pit_volume",
                     "mud_weight_in", "ecd", "gamma_ray", "gas_total", "rotary_rpm")
    @classmethod
    def reading_is_bounded(cls, value):
        # Input resource/numerical bound, not an equipment operating limit.
        if value > 1_000_000:
            raise ValueError("reading exceeds the supported prototype numeric range")
        return value

class RiskAssessmentResponse(BaseModel):
    alert_id: str
    well_id: str
    timestamp: str
    measured_depth: float
    alert_type: str
    severity: str
    lead_time_seconds: int
    lead_time_basis: str = "not_estimated"
    numeric_score_type: str = "uncalibrated_heuristic_score"
    method_version: str = "heuristic-risk-v1"
    confidence_score: float
    ml_probability: float
    physics_severity: float
    primary_mechanism: str
    driller_action_summary: str
    detailed_sop: List[str]
    historical_citations: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    well_id: str = "NHK-421"
    current_depth: float = Field(default=2845.0, ge=0, allow_inf_nan=False)
    formation: str = "Barail Coal-Shale"
    query: str = Field(min_length=1, max_length=2000)

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be blank")
        return value.strip()

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    engine: str
    evidence_count: int
