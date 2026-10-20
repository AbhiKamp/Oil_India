import os
import sys
import pytest

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import importlib.util

def load_mod(name, rel_path):
    full_path = os.path.join(base_dir, rel_path)
    spec = importlib.util.spec_from_file_location(name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

fusion_mod = load_mod("fusion_engine", "fusion_engine.py")

def test_risk_fusion_normal():
    engine = fusion_mod.RiskFusionEngine()
    ml_pred = {
        "ml_probabilities": {"normal": 0.85, "hole_packoff": 0.05, "differential_sticking": 0.05, "gas_kick": 0.02, "lost_circulation": 0.03},
        "features": {"spp_slope_psi_sec": 0.0, "flow_delta_lpm": 0.0}
    }
    physics = {}
    alert = engine.fuse_risk_assessment("NHK-421", 2800.0, "Tipam Sandstone", ml_pred, physics)
    assert alert["hazard_type"] == "NORMAL_DRILLING"
    assert alert["severity"] in ["INFO", "WATCH"]

def test_risk_fusion_packoff():
    engine = fusion_mod.RiskFusionEngine()
    ml_pred = {
        "ml_probabilities": {"normal": 0.10, "hole_packoff": 0.80, "differential_sticking": 0.05, "gas_kick": 0.02, "lost_circulation": 0.03},
        "features": {"spp_slope_psi_sec": 4.5, "flow_delta_lpm": -20.0}
    }
    physics = {}
    offset_chunks = [{"well_name": "MOR-118", "md_top": 2848.0}]
    alert = engine.fuse_risk_assessment("NHK-421", 2845.0, "Barail Coal-Shale", ml_pred, physics, offset_chunks)
    assert alert["hazard_type"] == "HOLE_PACKOFF"
    assert alert["severity"] in ["WARNING", "CRITICAL"]
    assert alert["confidence_score"] > 0.60
    assert len(alert["detailed_sop"]) >= 3
    assert "Review the hole packoff assessment" in alert["driller_action_summary"]
    assert "2,400" not in " ".join(alert["detailed_sop"])
    assert alert["lead_time_seconds"] == 0
    assert alert["lead_time_basis"] == "not_estimated"
    assert alert["numeric_score_type"] == "uncalibrated_heuristic_score"

def test_severity_does_not_claim_incident_countdown():
    severity, lead_time = fusion_mod.SeverityCalculator.calculate_severity(0.9, 0.9)
    assert severity == "CRITICAL"
    assert lead_time == 0


def test_same_observation_produces_stable_alert_identity_and_time():
    engine = fusion_mod.RiskFusionEngine()
    prediction = {
        "observation_timestamp": "2026-01-01T00:00:00+00:00",
        "ml_probabilities": {"normal": 0.9, "hole_packoff": 0.03, "differential_sticking": 0.02,
                             "gas_kick": 0.03, "lost_circulation": 0.02},
        "features": {"spp_slope_psi_sec": 0, "flow_delta_lpm": 0},
    }
    first = engine.fuse_risk_assessment("W1", 100, "F", prediction, {})
    second = engine.fuse_risk_assessment("W1", 100, "F", prediction, {})
    assert first["alert_id"] == second["alert_id"]
    assert first["timestamp"] == second["timestamp"] == prediction["observation_timestamp"]
    assert first["method_version"] == "heuristic-risk-v1"
