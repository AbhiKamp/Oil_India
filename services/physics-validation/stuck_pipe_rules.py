"""
StrataSentry-NWIS: Physics-Based Stuck Pipe Validation Rules
Validates differential sticking, mechanical pack-off, and keyseating against physical boundaries.
"""

from typing import Dict, Any

class StuckPipePhysicsRules:
    @staticmethod
    def evaluate_differential_sticking(
        overbalance_bar: float,
        contact_length_m: float,
        mudcake_friction_coeff: float = 0.15,
        stationary_time_min: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates theoretical pull force required to free differentially stuck string:
        F_pull = delta_P * Area_contact * mu_friction
        """
        # Area in sq meters (e.g. 5" drill collar touching over 10m length, contact width ~0.03m)
        contact_area_m2 = contact_length_m * 0.035
        # 1 bar = 100,000 N/m^2 = 100 kPa
        delta_p_pa = overbalance_bar * 1e5
        pull_force_n = delta_p_pa * contact_area_m2 * mudcake_friction_coeff
        pull_force_klbs = (pull_force_n / 4.44822) / 1000.0

        is_risk = overbalance_bar > 20.0 and stationary_time_min > 5.0
        return {
            "is_risk": is_risk,
            "overbalance_bar": round(overbalance_bar, 1),
            "estimated_pull_force_klbs": round(pull_force_klbs, 1),
            "rule_violated": "HIGH_OVERBALANCE_STATIONARY_COLLAR" if is_risk else "NONE"
        }

    @staticmethod
    def evaluate_packoff_mechanics(
        annular_pressure_surge_psi: float,
        rotary_torque_spike_pct: float,
        rop_drop_pct: float
    ) -> Dict[str, Any]:
        """
        Physical pack-off signature:
        Annular restriction -> Flow path constricted -> SPP surge + Torque surge + ROP collapse
        """
        is_packoff = annular_pressure_surge_psi > 250.0 and (rotary_torque_spike_pct > 30.0 or rop_drop_pct > 60.0)
        severity = 0.0
        if is_packoff:
            severity = min(1.0, (annular_pressure_surge_psi / 500.0) * 0.6 + (rotary_torque_spike_pct / 100.0) * 0.4)

        return {
            "is_packoff": is_packoff,
            "physics_severity": round(severity, 2),
            "mechanism": "ANNULAR_SOLIDS_BRIDGING" if is_packoff else "NORMAL_CUTTINGS_TRANSPORT"
        }
