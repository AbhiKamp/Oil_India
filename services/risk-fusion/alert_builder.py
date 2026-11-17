"""
StrataSentry-NWIS: Structured Alert Builder
Packages fused risk evaluations into standardized, schema-compliant RiskAlert objects.
"""

import hashlib
import json
from datetime import datetime, timezone
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
        citations: List[Dict[str, Any]] = None,
        observation_timestamp: str = None,
        method_version: str = "heuristic-risk-v1"
    ) -> Dict[str, Any]:
        """
        Builds standardized schema-compliant JSON alert payload.
        """
        action_summary = recommendations[0] if recommendations else "Maintain continuous monitoring."
        identity = json.dumps([
            well_id, observation_timestamp, round(measured_depth, 2), hazard_type, method_version
        ], separators=(",", ":"), ensure_ascii=True)
        return {
            "alert_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32],
            "well_id": well_id,
            "timestamp": observation_timestamp or datetime.now(timezone.utc).isoformat(),
            "method_version": method_version,
            "measured_depth": round(measured_depth, 2),
            "alert_type": hazard_type,
            "hazard_type": hazard_type,
            "severity": severity,
            "lead_time_seconds": lead_time_seconds,
            "lead_time_basis": "not_estimated",
            "confidence_score": round(confidence_score, 2),
            "ml_probability": round(ml_probability, 3),
            "numeric_score_type": "uncalibrated_heuristic_score",
            "physics_severity": round(physics_severity, 3),
            "primary_mechanism": mechanism,
            "driller_action_summary": action_summary,
            "detailed_sop": recommendations,
            "historical_citations": citations or []
        }
