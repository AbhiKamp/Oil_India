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

pred_mod = load_mod("predictor", "inference/predictor.py")

def test_risk_predictor_normal_drilling():
    predictor = pred_mod.DrillingRiskPredictor()
    window = [
        {
            "measured_depth": 2800.0 + i * 0.01,
            "rop": 14.0,
            "wob": 12.0,
            "surface_torque": 14.0,
            "rotary_rpm": 110,
            "standpipe_pressure": 2800.0,
            "flow_in": 2400.0,
            "flow_out_pct": 100.0,
            "pit_volume": 42.0,
            "mud_weight_in": 1.25,
            "ecd": 1.30,
            "gas_total": 12.0
        }
        for i in range(25)
    ]
    res = predictor.evaluate_window(window, formation="Tipam Sandstone")
    assert res["ml_probabilities"]["normal"] > 0.70
    assert res["ml_probabilities"]["hole_packoff"] < 0.20

def test_risk_predictor_packoff_detection():
    predictor = pred_mod.DrillingRiskPredictor()
    window = [
        {
            "measured_depth": 2845.0 + i * 0.005,
            "rop": max(2.0, 14.0 - i * 0.5), # Falling ROP
            "wob": 14.0,
            "surface_torque": 14.0 + (i % 5) * 1.8, # Erratic torque
            "rotary_rpm": 90,
            "standpipe_pressure": 2800.0 + i * 35.0, # Rapidly rising SPP
            "flow_in": 2400.0,
            "flow_out_pct": 70.0,
            "pit_volume": 41.8,
            "mud_weight_in": 1.28,
            "ecd": 1.38,
            "gas_total": 15.0
        }
        for i in range(25)
    ]
    res = predictor.evaluate_window(window, formation="Barail Coal-Shale")
    assert res["ml_probabilities"]["hole_packoff"] > 0.40
    assert res["ml_probabilities"]["hole_packoff"] > res["ml_probabilities"]["normal"]
