"""
StrataSentry-NWIS: Dynamic Equivalent Circulating Density (ECD)
Calculates dynamic downhole bottomhole pressure and cuttings loading effects.
"""

from typing import Dict, Any

class DynamicECDCalculator:
    @staticmethod
    def calculate_dynamic_ecd(
        static_mud_weight_sg: float,
        annular_pressure_loss_psi: float,
        tvd_m: float,
        cuttings_concentration_vol: float = 0.03, # 3% cuttings by volume
        rock_density_sg: float = 2.60
    ) -> Dict[str, float]:
        """
        ECD = Static_MW + (delta_P_annular / (0.0981 * TVD_m)) + Cuttings_Loading
        """
        if tvd_m <= 0:
            return {"ecd_sg": static_mud_weight_sg, "hydrostatic_bar": 0.0, "cuttings_effect_sg": 0.0}

        # Hydrostatic pressure gradient in bar / m: P_hyd = MW * 0.0981 * TVD
        # Convert psi to bar: 1 psi = 0.0689476 bar
        annular_loss_bar = annular_pressure_loss_psi * 0.0689476
        friction_ecd_sg = annular_loss_bar / (0.0981 * tvd_m)

        # Cuttings loading addition: Cv * (rho_rock - rho_mud) / (1 - Cv)
        cv = max(0.0, min(0.20, cuttings_concentration_vol))
        cuttings_effect_sg = (cv * (rock_density_sg - static_mud_weight_sg)) / max(0.01, (1.0 - cv))

        total_ecd = static_mud_weight_sg + friction_ecd_sg + cuttings_effect_sg
        bottomhole_pressure_bar = (total_ecd * 0.0981 * tvd_m)

        return {
            "ecd_sg": round(total_ecd, 3),
            "static_mw_sg": round(static_mud_weight_sg, 3),
            "friction_delta_sg": round(friction_ecd_sg, 3),
            "cuttings_delta_sg": round(cuttings_effect_sg, 3),
            "bottomhole_pressure_bar": round(bottomhole_pressure_bar, 1)
        }
