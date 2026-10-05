"""
StrataSentry-NWIS: End-to-End Pipeline Integration Test
Verifies telemetry stream -> ML feature extraction -> Physics evaluation -> Fusion -> Grounded RAG alert.
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.services.orchestrator import DomainOrchestrator

def test_full_operational_pipeline():
    orc = DomainOrchestrator()
    orc.stream_processor.buffer.clear()

    # 1. Ingest normal telemetry baseline
    for i in range(20):
        frame = {
            "well_id": "NHK-421",
            "measured_depth": 2840.0 + i * 0.1,
            "bit_depth": 2839.8 + i * 0.1,
            "rop": 14.0,
            "wob": 12.0,
            "surface_torque": 14.2,
            "rotary_rpm": 110,
            "standpipe_pressure": 2820.0,
            "flow_in": 2400.0,
            "flow_out_pct": 100.0,
            "pit_volume": 42.0,
            "mud_weight_in": 1.28,
            "ecd": 1.32,
            "gamma_ray": 85.0,
            "gas_total": 15.0
        }
        orc.ingest_telemetry_frame(frame)

    # 2. Check risk under normal drilling
    alert_normal = orc.evaluate_live_risk("NHK-421")
    assert alert_normal["severity"] in ["INFO", "WATCH"]

    # 3. Ingest severe pack-off divergence
    for i in range(25):
        frame = {
            "well_id": "NHK-421",
            "measured_depth": 2845.0 + i * 0.05,
            "bit_depth": 2844.8 + i * 0.05,
            "rop": max(1.0, 14.0 - i * 0.6), # ROP drops
            "wob": 15.0,
            "surface_torque": 14.2 + (i % 4) * 2.5, # Torque volatility
            "rotary_rpm": 85,
            "standpipe_pressure": 2820.0 + i * 40.0, # Rapid pressure surge
            "flow_in": 2400.0,
            "flow_out_pct": 70.0, # Annular flow restriction
            "pit_volume": 41.8,
            "mud_weight_in": 1.28,
            "ecd": 1.38,
            "gamma_ray": 105.0,
            "gas_total": 20.0
        }
        orc.ingest_telemetry_frame(frame)

    # 4. Check that risk elevates to WARNING or CRITICAL
    alert_packoff = orc.evaluate_live_risk("NHK-421")
    assert alert_packoff["hazard_type"] == "HOLE_PACKOFF"
    assert alert_packoff["severity"] in ["WARNING", "CRITICAL"]
    assert alert_packoff["confidence_score"] > 0.60
    assert len(alert_packoff["detailed_sop"]) >= 3
