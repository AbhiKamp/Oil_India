"""
StrataSentry-NWIS: Structured Alert Builder
Packages fused risk evaluations into standardized, schema-compliant RiskAlert objects.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

class AlertBuilder:
    @staticmethod
    def create_alert(
        well_id: str,
        measured_depth: float,
        hazard_type: str,
        severity: str,
        lead_time_seconds: int,
        confidence_score: float,
        ml_probability: float,
        physics_severity: float,
        mechanism: str,
        recommendations: List[str],
        citations: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Builds standardized schema-compliant JSON alert payload.
        """
        action_summary = recommendations[0] if recommendations else "Maintain continuous monitoring."
        return {
            "alert_id": str(uuid.uuid4()),
            "well_id": well_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "measured_depth": round(measured_depth, 2),
            "alert_type": hazard_type,
            "hazard_type": hazard_type,
            "severity": severity,
            "lead_time_seconds": lead_time_seconds,
            "confidence_score": round(confidence_score, 2),
            "ml_probability": round(ml_probability, 3),
            "physics_severity": round(physics_severity, 3),
            "primary_mechanism": mechanism,
            "driller_action_summary": action_summary,
            "detailed_sop": recommendations,
            "historical_citations": citations or []
        }
