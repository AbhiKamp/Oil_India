"""
StrataSentry-NWIS: Telemetry Stream Processor
Maintains an in-memory sliding buffer and computes rolling temporal derivatives.
"""

from collections import deque
from typing import Dict, Any, List, Optional
import numpy as np

class TelemetryStreamProcessor:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def process_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends frame to buffer and computes rolling derivatives.
        """
        self.buffer.append(frame)
        derivatives = self._compute_derivatives()
        enriched_frame = dict(frame)
        enriched_frame.update(derivatives)
        return enriched_frame

    def _compute_derivatives(self) -> Dict[str, float]:
        if len(self.buffer) < 5:
            return {
                "spp_rate_of_change_psi_sec": 0.0,
                "torque_std_30s": 0.0,
                "flow_delta": 0.0,
                "mse_mepa": 0.0
            }

        spp_vals = [f["standpipe_pressure"] for f in self.buffer]
        torque_vals = [f["surface_torque"] for f in self.buffer]
        rop = self.buffer[-1]["rop"]
        wob = self.buffer[-1]["wob"]
        rpm = self.buffer[-1]["rotary_rpm"]
        torque = self.buffer[-1]["surface_torque"]

        # SPP slope over last 10 points
        spp_subset = spp_vals[-10:]
        spp_slope = float(np.polyfit(range(len(spp_subset)), spp_subset, 1)[0]) if len(spp_subset) >= 2 else 0.0

        # Torque standard deviation
        torque_std = float(np.std(torque_vals[-30:])) if len(torque_vals) >= 2 else 0.0

        # Mechanical Specific Energy (Teale MSE)
        # MSE = (WOB / A_bit) + (120 * pi * RPM * Torque) / (A_bit * ROP)
        # Approximate for 8.5" bit: Area = 56.74 sq in
        bit_area_sq_in = 56.74
        if rop > 0.1:
            mse_val = (wob * 2204.62 / bit_area_sq_in) + (120 * np.pi * rpm * (torque * 737.56)) / (bit_area_sq_in * (rop * 3.28084))
            mse_val = mse_val / 1000.0 # Convert to ksi
        else:
            mse_val = 0.0

        return {
            "spp_rate_of_change_psi_sec": round(spp_slope, 2),
            "torque_std_30s": round(torque_std, 2),
            "flow_delta": round(self.buffer[-1]["flow_in"] * (self.buffer[-1]["flow_out_pct"] / 100.0 - 1.0), 1),
            "mse_ksi": round(mse_val, 2)
        }

    def get_recent_history(self, count: int = 30) -> List[Dict[str, Any]]:
        return list(self.buffer)[-count:]
