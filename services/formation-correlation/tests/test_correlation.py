import os
import sys
import pytest
import numpy as np

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

prep_mod = load_mod("log_preprocessing", "log_preprocessing.py")
dtw_mod = load_mod("dtw_alignment", "dtw_alignment.py")
gr_mod = load_mod("gamma_ray_alignment", "gamma_ray_alignment.py")
matcher_mod = load_mod("formation_matcher", "formation_matcher.py")

def test_log_preprocessing():
    prep = prep_mod.LogPreprocessor()
    vals = [40.0, 50.0, 100.0, 200.0]
    norm = prep.despike_and_normalize(vals, 0.0, 200.0)
    assert norm[0] == 0.2
    assert norm[-1] == 1.0

def test_dtw_exact_match():
    dtw = dtw_mod.DynamicTimeWarpingAligner()
    seq = np.array([0.1, 0.5, 0.9, 0.4, 0.2])
    res = dtw.align(seq, seq)
    assert res["distance"] == 0.0
    assert res["similarity_score"] == 1.0

def test_formation_matcher():
    matcher = matcher_mod.FormationMatcher()
    offset_tops = [
        {"formation_name": "Barail Coal-Shale", "md_top": 2850.0, "primary_lithology": "Coal/Shale"}
    ]
    # Depth shift = +10m (formation is 10m shallower in active well)
    preds = matcher.predict_formation_tops_ahead_of_bit(
        current_md=2800.0,
        depth_shift_m=10.0,
        offset_tops=offset_tops
    )
    assert len(preds) == 1
    assert preds[0]["predicted_entry_md"] == 2840.0
    assert preds[0]["distance_to_boundary_m"] == 40.0
    assert preds[0]["status"] == "AHEAD_OF_BIT"
