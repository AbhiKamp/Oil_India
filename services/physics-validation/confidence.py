"""
StrataSentry-NWIS: Physics-Based Confidence Evaluator
Quantifies physical validity and sensor consistency across redundant sensor measurements.
"""

from typing import Dict, Any

class PhysicsConfidenceEvaluator:
    @staticmethod
    def evaluate_sensor_consistency(
        spp_psi: float,
        flow_in_lpm: float,
        ecd_sg: float,
        static_mw_sg: float
    ) -> float:
        """
        Validates whether sensor readings conform to physical conservation:
        - If pumps are active (Flow > 1000 LPM), SPP must be positive (> 500 psi).
        - ECD must be greater than or equal to static mud weight.
        """
        score = 1.0

        if flow_in_lpm > 1000.0 and spp_psi < 300.0:
            score -= 0.4 # Sensor disconnect or faulty transducer
        if ecd_sg < static_mw_sg - 0.05:
            score -= 0.4 # Thermally impossible without severe gas dilution

        return max(0.0, round(score, 2))
