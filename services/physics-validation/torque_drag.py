"""
StrataSentry-NWIS: Soft-String 3D Torque & Drag Model
Calculates theoretical hookload, rotary torque, and back-calculates friction factors.
"""

import math
from typing import List, Dict, Any

class SoftStringTorqueDragModel:
    @staticmethod
    def calculate_tension_and_torque(
        trajectory_stations: List[Dict[str, Any]],
        drillstring_unit_weight_kg_m: float = 30.0,
        mud_weight_sg: float = 1.28,
        friction_coeff: float = 0.25,
        bit_wob_tons: float = 12.0
    ) -> Dict[str, float]:
        """
        Calculates theoretical surface hookload and rotary torque for rotating off-bottom / on-bottom.
        Buoyancy factor: BF = 1 - (MW / 7.85) (for steel in drilling mud)
        """
        bf = 1.0 - (mud_weight_sg / 7.85)
        buoyed_weight_per_m = drillstring_unit_weight_kg_m * bf # kg/m

        total_md = trajectory_stations[-1]["measured_depth"] if trajectory_stations else 3000.0
        # Basic cumulative normal force summation
        total_string_weight_kn = (total_md * buoyed_weight_per_m * 9.81) / 1000.0

        # Normal contact force accumulation based on dogleg severity
        total_dogleg_rad = 0.0
        for s in trajectory_stations:
            total_dogleg_rad += math.radians(s.get("dogleg_severity", 0.0) / 30.0 * 10.0)

        # Capstan friction amplification: T_top = T_bottom * exp(mu * total_angle) + W_buoyed
        tension_kn = total_string_weight_kn * math.exp(friction_coeff * total_dogleg_rad)
        surface_hookload_tons = tension_kn / 9.81

        # Surface torque estimation: Torque = mu * Normal_Force * r_pipe
        pipe_radius_m = 0.127 / 2.0 # 5" pipe
        torque_kn_m = friction_coeff * tension_kn * pipe_radius_m

        return {
            "buoyancy_factor": round(bf, 3),
            "theoretical_hookload_tons": round(surface_hookload_tons, 1),
            "theoretical_torque_kn_m": round(torque_kn_m, 2),
            "effective_friction_coeff": round(friction_coeff, 3)
        }
