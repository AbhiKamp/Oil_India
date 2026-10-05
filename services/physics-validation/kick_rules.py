"""
StrataSentry-NWIS: Physics-Based Kick & Well Control Rules
Evaluates mass conservation (Flow In vs Flow Out) and pit volume accumulation.
"""

from typing import Dict, Any

class KickPhysicsRules:
    @staticmethod
    def evaluate_influx_mass_balance(
        flow_in_lpm: float,
        flow_out_lpm: float,
        pit_rate_lpm: float,
        pumps_active: bool = True
    ) -> Dict[str, Any]:
        """
        Mass conservation check:
        Net accumulation = Flow Out - Flow In.
        If Pumps Off and Flow Out > 0 -> Active Influx (KICK).
        """
        if not pumps_active and flow_out_lpm > 10.0:
            return {
                "kick_detected": True,
                "severity": "CRITICAL",
                "influx_rate_lpm": round(flow_out_lpm, 1),
                "mechanism": "FLOW_CHECK_FAILED_WELL_FLOWING"
            }

        delta_flow = flow_out_lpm - flow_in_lpm
        kick_detected = delta_flow > 120.0 and pit_rate_lpm > 80.0

        return {
            "kick_detected": kick_detected,
            "severity": "CRITICAL" if kick_detected else "NORMAL",
            "delta_flow_lpm": round(delta_flow, 1),
            "pit_gain_rate_lpm": round(pit_rate_lpm, 1),
            "mechanism": "PORE_PRESSURE_OVERBALANCE_LOSS" if kick_detected else "STABLE_MASS_BALANCE"
        }
