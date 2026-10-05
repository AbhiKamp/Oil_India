"""
StrataSentry-NWIS: Drilling Feature Engineering
Computes physical petroleum indicators: MSE, d-exponent, SPP derivative, torque variance.
"""

import math
import numpy as np
from typing import Dict, Any, List

class DrillingFeatureEngineer:
    def __init__(self, bit_diameter_in: float = 8.5):
        self.bit_diameter = bit_diameter_in
        self.bit_area = math.pi * (bit_diameter_in / 2.0) ** 2 # sq inches (e.g. 56.74 sq in for 8.5" bit)

    def extract_features(self, telemetry_window: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculates 12 engineered features from a window of recent telemetry frames.
        """
        if not telemetry_window:
            return {}

        current = telemetry_window[-1]
        rop = current.get("rop", 0.0)
        wob = current.get("wob", 0.0)
        rpm = current.get("rotary_rpm", 0.0)
        torque = current.get("surface_torque", 0.0)
        spp = current.get("standpipe_pressure", 0.0)
        flow_in = current.get("flow_in", 0.0)
        flow_out_pct = current.get("flow_out_pct", 0.0)
        pit_vol = current.get("pit_volume", 0.0)
        mw = current.get("mud_weight_in", 1.25)

        # 1. Teale Mechanical Specific Energy (MSE) in ksi
        if rop > 0.1 and rpm > 0:
            # WOB in lbs (1 metric ton = 2204.62 lbs), Torque in ft-lbs (1 kNm = 737.56 ft-lbs)
            wob_lbs = wob * 2204.62
            torque_ft_lbs = torque * 737.56
            rop_ft_hr = rop * 3.28084
            mse = (wob_lbs / self.bit_area) + (120 * math.pi * rpm * torque_ft_lbs) / (self.bit_area * rop_ft_hr)
            mse_ksi = mse / 1000.0
        else:
            mse_ksi = 0.0

        # 2. Corrected d-exponent (Jordan & Shirley formulation)
        if rop > 0.1 and rpm > 0 and wob > 0.1:
            try:
                num = math.log10(rop / (60.0 * rpm))
                denom = math.log10((12.0 * wob * 2204.62) / (1e6 * self.bit_diameter))
                d_exp_raw = num / denom
                # Normal mud weight baseline 1.07 SG (9.0 ppg)
                d_exp = d_exp_raw * (1.07 / mw)
            except Exception:
                d_exp = 1.0
        else:
            d_exp = 1.0

        # 3. SPP slope (rate of change in psi/sec)
        spp_vals = [f.get("standpipe_pressure", spp) for f in telemetry_window[-15:]]
        if len(spp_vals) >= 2:
            spp_slope = float(np.polyfit(range(len(spp_vals)), spp_vals, 1)[0])
        else:
            spp_slope = 0.0

        # 4. Torque standard deviation
        torque_vals = [f.get("surface_torque", torque) for f in telemetry_window[-20:]]
        torque_std = float(np.std(torque_vals)) if len(torque_vals) >= 2 else 0.0

        # 5. Flow Delta (L/min)
        flow_delta = flow_in * (flow_out_pct / 100.0 - 1.0)

        # 6. Pit volume rate of change (m^3 / min)
        pit_vals = [f.get("pit_volume", pit_vol) for f in telemetry_window[-20:]]
        pit_slope = float(np.polyfit(range(len(pit_vals)), pit_vals, 1)[0]) * 60.0 if len(pit_vals) >= 2 else 0.0

        return {
            "mse_ksi": round(mse_ksi, 2),
            "d_exponent": round(d_exp, 3),
            "spp_slope_psi_sec": round(spp_slope, 2),
            "torque_std": round(torque_std, 2),
            "flow_delta_lpm": round(flow_delta, 1),
            "pit_rate_m3_min": round(pit_slope, 3),
            "rop": rop,
            "wob": wob,
            "rpm": rpm,
            "spp": spp,
            "torque": torque,
            "ecd": current.get("ecd", mw)
        }
