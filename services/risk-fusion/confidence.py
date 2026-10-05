"""
StrataSentry-NWIS: Multi-Modal Risk Confidence Evaluator
Quantifies overall decision confidence combining ML entropy, physics agreement, and historical evidence.
"""

from typing import Dict, Any

class FusedConfidenceEvaluator:
    @staticmethod
    def calculate_fused_confidence(
        ml_probability: float,
        physics_confirmed: bool,
        historical_citation_found: bool,
        sensor_integrity: float = 1.0
    ) -> float:
        """
        Calculates unified decision confidence score (0.0 to 1.0).
        """
        score = 0.40 # Base
        # ML confidence based on margin above uncertainty (0.5)
        score += max(0.0, (ml_probability - 0.5) * 0.40)
        # Physics confirmation adds high trust
        if physics_confirmed:
            score += 0.20
        # Historical precedent adds calibration
        if historical_citation_found:
            score += 0.15

        # Scaled by sensor integrity
        final_score = score * sensor_integrity
        return min(1.0, max(0.1, round(final_score, 2)))
