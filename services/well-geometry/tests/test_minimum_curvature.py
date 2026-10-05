import pytest
import os
import sys
import importlib.util

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def load_mod(name, rel_path):
    full_path = os.path.join(base_dir, rel_path)
    spec = importlib.util.spec_from_file_location(name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mcm_mod = load_mod("minimum_curvature", "minimum_curvature.py")
traj_mod = load_mod("trajectory_builder", "trajectory_builder.py")
tvd_mod = load_mod("tvd_calculator", "tvd_calculator.py")

def test_vertical_section_mcm():
    calc = mcm_mod.MinimumCurvatureCalculator()
    # Vertical section from 0 to 100m MD with zero inclination
    res = calc.calculate_station(
        md1=0.0, inc1_deg=0.0, azi1_deg=0.0,
        md2=100.0, inc2_deg=0.0, azi2_deg=0.0
    )
    assert res["tvd"] == 100.0
    assert res["north"] == 0.0
    assert res["east"] == 0.0
    assert res["dogleg_severity_deg_30m"] == 0.0

def test_deviated_build_section():
    calc = mcm_mod.MinimumCurvatureCalculator()
    # Build from 0 to 10 deg over 100m at 90 deg azimuth (East)
    res = calc.calculate_station(
        md1=0.0, inc1_deg=0.0, azi1_deg=90.0,
        md2=100.0, inc2_deg=10.0, azi2_deg=90.0
    )
    assert res["tvd"] > 99.0
    assert res["east"] > 8.0
    assert res["north"] == 0.0
    assert round(res["dogleg_severity_deg_30m"], 1) == 3.0

def test_tvd_interpolation():
    trajectory = [
        {"measured_depth": 0.0, "true_vertical_depth": 0.0},
        {"measured_depth": 1000.0, "true_vertical_depth": 1000.0},
        {"measured_depth": 2000.0, "true_vertical_depth": 1950.0}
    ]
    tvd = tvd_mod.TVDCalculator.interpolate_tvd(1500.0, trajectory)
    assert tvd == 1475.0
