"""
StrataSentry-NWIS: Drilling Hydraulics (Bingham Plastic Formulation)
Calculates annular pressure drops, Reynolds numbers, and frictional losses.
"""

import math
from typing import Dict, Any

class BinghamPlasticHydraulics:
    @staticmethod
    def calculate_annular_pressure_loss(
        flow_rate_lpm: float,
        hole_diameter_in: float,
        pipe_od_in: float,
        tvd_m: float,
        plastic_viscosity_cp: float = 22.0,
        yield_point_lbf_100sqft: float = 18.0,
        mud_weight_sg: float = 1.28
    ) -> Dict[str, float]:
        """
        Calculates annular velocity, flow regime, and frictional pressure loss in psi.
        """
        # Convert LPM to GPM
        q_gpm = flow_rate_lpm / 3.78541
        tvd_ft = tvd_m * 3.28084
        dh = hole_diameter_in
        dp = pipe_od_in

        # Annular cross section area: Dh^2 - Dp^2
        area_diff = dh**2 - dp**2
        if area_diff <= 0:
            return {"annular_velocity_ft_min": 0.0, "pressure_loss_psi": 0.0, "regime": "UNDEFINED"}

        # Annular velocity in ft/min
        v_ann = (24.51 * q_gpm) / area_diff

        # Critical velocity for Bingham Plastic
        # Vc = (97 * PV + 97 * sqrt(PV^2 + 8.2 * rho * Dh_Dp^2 * YP)) / (rho * Dh_Dp)
        dh_minus_dp = dh - dp
        rho_ppg = mud_weight_sg / 0.119826

        # Frictional pressure loss in laminar flow (psi)
        # delta_P = [ (PV * V_ann) / (60,000 * (Dh - Dp)^2) + YP / (200 * (Dh - Dp)) ] * TVD_ft
        dp_friction = (
            (plastic_viscosity_cp * v_ann) / (60000.0 * (dh_minus_dp**2)) +
            yield_point_lbf_100sqft / (200.0 * dh_minus_dp)
        ) * tvd_ft

        return {
            "annular_velocity_ft_min": round(v_ann, 1),
            "annular_velocity_m_sec": round(v_ann * 0.00508, 2),
            "annular_pressure_loss_psi": round(dp_friction, 1),
            "regime": "LAMINAR" if v_ann < 350.0 else "TURBULENT"
        }
