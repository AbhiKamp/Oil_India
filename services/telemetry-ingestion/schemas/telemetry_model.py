"""
StrataSentry-NWIS: Telemetry Ingestion Pydantic Data Models
Defines high-frequency drilling telemetry frames and validation constraints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DrillingTelemetryPacket(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    well_id: str
    measured_depth: float = Field(..., ge=0.0, description="Measured Depth (m)")
    bit_depth: float = Field(..., ge=0.0, description="Bit Depth (m)")
    rop: float = Field(0.0, ge=0.0, description="Rate of Penetration (m/hr)")
    wob: float = Field(0.0, ge=0.0, description="Weight on Bit (metric tons)")
    surface_torque: float = Field(0.0, ge=0.0, description="Surface Torque (kN.m)")
    rotary_rpm: float = Field(0.0, ge=0.0, description="Rotary RPM")
    standpipe_pressure: float = Field(..., ge=0.0, description="Standpipe Pressure (psi)")
    flow_in: float = Field(..., ge=0.0, description="Mud Flow In (L/min)")
    flow_out_pct: float = Field(0.0, ge=0.0, description="Flow Out (%)")
    pit_volume: float = Field(0.0, ge=0.0, description="Pit Volume (m^3)")
    mud_weight_in: float = Field(1.25, ge=0.5, le=3.0, description="Mud Density In (SG)")
    ecd: float = Field(1.30, ge=0.5, le=3.5, description="Equivalent Circulating Density (SG)")
    gamma_ray: float = Field(0.0, ge=0.0, description="Gamma Ray (API)")
    gas_total: float = Field(0.0, ge=0.0, description="Total Gas Units")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
