"""
StrataSentry-NWIS: Minimum Curvature Method (MCM) Algorithm
Industry standard 3D directional survey trajectory calculation according to API Bull D20.
"""

import math
from typing import Dict, Any, Tuple

class MinimumCurvatureCalculator:
    @staticmethod
    def calculate_station(
        md1: float, inc1_deg: float, azi1_deg: float,
        md2: float, inc2_deg: float, azi2_deg: float,
        tvd1: float = 0.0, north1: float = 0.0, east1: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculates station 2 position given station 1 and survey measurements.
        """
        delta_md = md2 - md1
        if delta_md <= 0.0:
            return {
                "tvd": tvd1, "north": north1, "east": east1,
                "delta_tvd": 0.0, "delta_north": 0.0, "delta_east": 0.0,
                "dogleg_angle_rad": 0.0, "dogleg_severity_deg_30m": 0.0,
                "ratio_factor": 1.0
            }

        # Convert to radians
        i1 = math.radians(inc1_deg)
        i2 = math.radians(inc2_deg)
        a1 = math.radians(azi1_deg)
        a2 = math.radians(azi2_deg)

        # Dogleg angle beta:
        # cos(beta) = cos(I1)*cos(I2) + sin(I1)*sin(I2)*cos(A2 - A1)
        cos_beta = math.cos(i1) * math.cos(i2) + math.sin(i1) * math.sin(i2) * math.cos(a2 - a1)
        # Numerical clamp for floating point inaccuracies
        cos_beta = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta)

        # Ratio factor F:
        if abs(beta) < 1e-6:
            f = 1.0
        else:
            f = (2.0 / beta) * math.tan(beta / 2.0)

        # Coordinate deltas
        delta_tvd = (delta_md / 2.0) * (math.cos(i1) + math.cos(i2)) * f
        delta_north = (delta_md / 2.0) * (math.sin(i1) * math.cos(a1) + math.sin(i2) * math.cos(a2)) * f
        delta_east = (delta_md / 2.0) * (math.sin(i1) * math.sin(a1) + math.sin(i2) * math.sin(a2)) * f

        # Dogleg severity in deg / 30m
        dls = (math.degrees(beta) / delta_md) * 30.0

        return {
            "tvd": round(tvd1 + delta_tvd, 3),
            "north": round(north1 + delta_north, 3),
            "east": round(east1 + delta_east, 3),
            "delta_tvd": round(delta_tvd, 3),
            "delta_north": round(delta_north, 3),
            "delta_east": round(delta_east, 3),
            "dogleg_angle_rad": round(beta, 5),
            "dogleg_severity_deg_30m": round(dls, 3),
            "ratio_factor": round(f, 5)
        }
