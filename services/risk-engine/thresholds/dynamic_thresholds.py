"""
StrataSentry-NWIS: Dynamic Drilling Thresholds
Computes adaptive alarm limits based on formation type, depth, and historical noise.
"""

from typing import Dict, Any

class DynamicThresholdManager:
    @staticmethod
    def get_thresholds(formation: str, depth_md: float) -> Dict[str, float]:
        """
        Adapts thresholds: in Barail coals and Kopili shales, tolerance for SPP surges
        and torque fluctuations is significantly tighter than in Tipam sands.
        """
        # Default baseline
        limits = {
            "max_spp_slope_psi_sec": 3.0,
            "max_torque_std": 3.5,
            "max_ecd_sg": 1.45,
            "max_pit_gain_rate_m3_min": 0.05
        }

        if "Barail" in formation:
            # Coal caving prone: strict packoff limits
            limits["max_spp_slope_psi_sec"] = 2.0
            limits["max_torque_std"] = 2.2
        elif "Kopili" in formation:
            # Overpressure shale: strict gas kick and borehole collapse limits
            limits["max_pit_gain_rate_m3_min"] = 0.03
            limits["max_ecd_sg"] = 1.50
        elif "Tipam" in formation:
            # Depleted porous sands: strict ECD overbalance limit to prevent differential sticking
            limits["max_ecd_sg"] = 1.35

        return limits
