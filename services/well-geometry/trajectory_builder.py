"""
StrataSentry-NWIS: Wellbore Trajectory Builder
Builds complete 3D wellbore paths from survey stations and converts to GeoJSON and 3D Linestrings.
"""

from typing import List, Dict, Any
try:
    from .minimum_curvature import MinimumCurvatureCalculator
except ImportError:
    from minimum_curvature import MinimumCurvatureCalculator

class TrajectoryBuilder:
    def __init__(self, calc: MinimumCurvatureCalculator = None):
        self.calc = calc or MinimumCurvatureCalculator()

    def build_trajectory(self, surveys: List[Dict[str, float]], surface_lat: float = 27.2842, surface_lon: float = 95.3418) -> List[Dict[str, Any]]:
        """
        Takes raw surveys [{"measured_depth": 0, "inclination_deg": 0, "azimuth_deg": 0}, ...]
        Returns full calculated trajectory points.
        """
        if not surveys:
            return []

        # Sort by MD
        sorted_surveys = sorted(surveys, key=lambda s: s["measured_depth"])
        trajectory = []

        # First station at surface
        first = sorted_surveys[0]
        cur_tvd = 0.0
        cur_north = 0.0
        cur_east = 0.0

        trajectory.append({
            "station_index": 0,
            "measured_depth": first["measured_depth"],
            "inclination_deg": first["inclination_deg"],
            "azimuth_deg": first["azimuth_deg"],
            "true_vertical_depth": cur_tvd,
            "northing_delta": cur_north,
            "easting_delta": cur_east,
            "dogleg_severity": 0.0,
            "closure_distance": 0.0
        })

        for i in range(1, len(sorted_surveys)):
            s1 = sorted_surveys[i - 1]
            s2 = sorted_surveys[i]

            res = self.calc.calculate_station(
                md1=s1["measured_depth"], inc1_deg=s1["inclination_deg"], azi1_deg=s1["azimuth_deg"],
                md2=s2["measured_depth"], inc2_deg=s2["inclination_deg"], azi2_deg=s2["azimuth_deg"],
                tvd1=cur_tvd, north1=cur_north, east1=cur_east
            )

            cur_tvd = res["tvd"]
            cur_north = res["north"]
            cur_east = res["east"]
            closure = (cur_north**2 + cur_east**2)**0.5

            trajectory.append({
                "station_index": i,
                "measured_depth": s2["measured_depth"],
                "inclination_deg": s2["inclination_deg"],
                "azimuth_deg": s2["azimuth_deg"],
                "true_vertical_depth": cur_tvd,
                "northing_delta": cur_north,
                "easting_delta": cur_east,
                "dogleg_severity": res["dogleg_severity_deg_30m"],
                "closure_distance": round(closure, 2)
            })

        return trajectory
