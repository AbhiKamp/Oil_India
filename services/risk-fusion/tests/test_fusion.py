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
    assert "Stop drilling ahead" in alert["driller_action_summary"]
