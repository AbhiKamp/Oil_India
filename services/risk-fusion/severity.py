"""
StrataSentry-NWIS: Severity Index Calculator
Determines alert severity level: INFO, WATCH, WARNING, CRITICAL.
"""

from typing import Dict, Any, Tuple

class SeverityCalculator:
    @staticmethod
    def calculate_severity(
        ml_probability: float,
        physics_severity: float,
        historical_offset_match: bool = False
    ) -> Tuple[str, int]:
        """
        Fuses:
        Combined Score = 0.50 * ML_prob + 0.40 * Physics_sev + 0.10 * Offset_precedent
        Returns (Severity_Label, Lead_Time_Seconds)
        """
        offset_score = 1.0 if historical_offset_match else 0.0
        fused = 0.50 * ml_probability + 0.40 * physics_severity + 0.10 * offset_score

        if fused >= 0.70:
            return "CRITICAL", 300   # 5 minutes to catastrophic event
        elif fused >= 0.45:
            return "WARNING", 900    # 15 minutes to escalation
        elif fused >= 0.25:
            return "WATCH", 1800     # 30 minutes early precursor
        else:
            return "INFO", 3600      # Normal operations advisory
