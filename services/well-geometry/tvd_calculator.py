"""
StrataSentry-NWIS: TVD Calculator
Interpolates True Vertical Depth for arbitrary Measured Depths along a trajectory.
"""

from typing import List, Dict, Any

class TVDCalculator:
    @staticmethod
    def interpolate_tvd(measured_depth: float, trajectory: List[Dict[str, Any]]) -> float:
        """
        Given a calculated trajectory, finds the TVD corresponding to any target MD.
        """
        if not trajectory:
            return measured_depth

        if measured_depth <= trajectory[0]["measured_depth"]:
            return trajectory[0]["true_vertical_depth"]

        if measured_depth >= trajectory[-1]["measured_depth"]:
            return trajectory[-1]["true_vertical_depth"]

        for i in range(1, len(trajectory)):
            s1 = trajectory[i - 1]
            s2 = trajectory[i]
            if s1["measured_depth"] <= measured_depth <= s2["measured_depth"]:
                md_span = s2["measured_depth"] - s1["measured_depth"]
                if md_span == 0:
                    return s1["true_vertical_depth"]
                fraction = (measured_depth - s1["measured_depth"]) / md_span
                return round(s1["true_vertical_depth"] + fraction * (s2["true_vertical_depth"] - s1["true_vertical_depth"]), 2)

        return measured_depth
