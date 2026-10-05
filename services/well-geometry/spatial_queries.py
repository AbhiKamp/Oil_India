"""
StrataSentry-NWIS: Wellbore Spatial Proximity & Collision Queries
Calculates 3D spatial distances between active drill-string position and offset wellbores.
"""

import math
from typing import List, Dict, Any

class WellboreSpatialQueries:
    @staticmethod
    def calculate_3d_distance(p1: Dict[str, float], p2: Dict[str, float]) -> float:
        """
        p1 and p2 have keys: 'tvd', 'north', 'east'
        """
        dn = p1.get("north", 0.0) - p2.get("north", 0.0)
        de = p1.get("east", 0.0) - p2.get("east", 0.0)
        dz = p1.get("tvd", 0.0) - p2.get("tvd", 0.0)
        return round(math.sqrt(dn**2 + de**2 + dz**2), 2)

    @staticmethod
    def find_nearest_offset_point(
        bit_point: Dict[str, float],
        offset_trajectory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identifies the closest station on an offset wellbore to the active bit.
        """
        min_dist = float("inf")
        nearest_station = None

        for station in offset_trajectory:
            pt = {
                "tvd": station.get("true_vertical_depth", 0.0),
                "north": station.get("northing_delta", 0.0),
                "east": station.get("easting_delta", 0.0)
            }
            d = WellboreSpatialQueries.calculate_3d_distance(bit_point, pt)
            if d < min_dist:
                min_dist = d
                nearest_station = station

        return {
            "minimum_distance_m": min_dist,
            "offset_station": nearest_station
        }
