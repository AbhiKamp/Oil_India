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

hyd_mod = load_mod("hydraulics", "hydraulics.py")
ecd_mod = load_mod("ecd", "ecd.py")
stuck_mod = load_mod("stuck_pipe_rules", "stuck_pipe_rules.py")
kick_mod = load_mod("kick_rules", "kick_rules.py")

def test_bingham_hydraulics_annular_pressure():
    hyd = hyd_mod.BinghamPlasticHydraulics()
    # 2400 LPM in 8.5" hole with 5" drill pipe at 2800m TVD
    res = hyd.calculate_annular_pressure_loss(
        flow_rate_lpm=2400.0,
        hole_diameter_in=8.5,
        pipe_od_in=5.0,
        tvd_m=2800.0,
        plastic_viscosity_cp=20.0,
        yield_point_lbf_100sqft=16.0
    )
    assert res["annular_velocity_ft_min"] > 100.0
    assert res["annular_pressure_loss_psi"] > 100.0
    assert res["regime"] == "LAMINAR"

def test_dynamic_ecd():
    ecd_calc = ecd_mod.DynamicECDCalculator()
    res = ecd_calc.calculate_dynamic_ecd(
        static_mud_weight_sg=1.28,
        annular_pressure_loss_psi=350.0,
        tvd_m=2800.0,
        cuttings_concentration_vol=0.04
    )
    assert res["ecd_sg"] > 1.28
    assert res["friction_delta_sg"] > 0.0
    assert res["cuttings_delta_sg"] > 0.0

def test_kick_physics_rules():
    rules = kick_mod.KickPhysicsRules()
    # Influx: flow out (2800 LPM) > flow in (2400 LPM) + pit gain 150 LPM
    res = rules.evaluate_influx_mass_balance(
        flow_in_lpm=2400.0,
        flow_out_lpm=2800.0,
        pit_rate_lpm=150.0,
        pumps_active=True
    )
    assert res["kick_detected"] is True
    assert res["severity"] == "CRITICAL"
