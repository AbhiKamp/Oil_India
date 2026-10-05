"""
StrataSentry-NWIS: Master Risk Fusion Engine
Performs Bayesian and weighted fusion of ML anomaly scores, physics rule violations, and offset historical precedent.
"""

from typing import Dict, Any, List, Optional
try:
    from .severity import SeverityCalculator
    from .confidence import FusedConfidenceEvaluator
    from .recommendation_builder import DrillerRecommendationBuilder
    from .alert_builder import AlertBuilder
except (ImportError, ValueError):
    from severity import SeverityCalculator
    from confidence import FusedConfidenceEvaluator
    from recommendation_builder import DrillerRecommendationBuilder
    from alert_builder import AlertBuilder

class RiskFusionEngine:
    def __init__(self):
        self.severity_calc = SeverityCalculator()
        self.confidence_eval = FusedConfidenceEvaluator()
        self.rec_builder = DrillerRecommendationBuilder()
        self.alert_builder = AlertBuilder()

    def fuse_risk_assessment(
        self,
        well_id: str,
        measured_depth: float,
        formation: str,
        ml_prediction: Dict[str, Any],
        physics_validation: Dict[str, Any],
        offset_evidence: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Integrates multi-domain signals into a unified operational alert.
        """
        ml_probs = ml_prediction.get("ml_probabilities", {"normal": 0.95})
        features = ml_prediction.get("features", {})
        has_offset = bool(offset_evidence and len(offset_evidence) > 0)

        # 1. Determine dominant hazard from ML
        hazards = {
            "HOLE_PACKOFF": ml_probs.get("hole_packoff", 0.0),
            "DIFFERENTIAL_STICKING": ml_probs.get("differential_sticking", 0.0),
            "GAS_KICK": ml_probs.get("gas_kick", 0.0),
            "LOST_CIRCULATION": ml_probs.get("lost_circulation", 0.0)
        }
        dominant_hazard = max(hazards, key=hazards.get)
        dominant_prob = hazards[dominant_hazard]

        # 2. Physics validation correlation
        physics_severity = 0.0
        mechanism = "NORMAL_CONDITIONS"

        if dominant_hazard == "HOLE_PACKOFF":
            # Check annular pressure surge
            spp_slope = features.get("spp_slope_psi_sec", 0.0)
            if spp_slope > 2.0:
                physics_severity = min(1.0, 0.4 + (spp_slope / 10.0) * 0.5)
                mechanism = "ANNULAR_CUTTINGS_ACCUMULATION_AND_COAL_CAVING"
        elif dominant_hazard == "GAS_KICK":
            flow_delta = features.get("flow_delta_lpm", 0.0)
            if flow_delta > 100.0:
                physics_severity = min(1.0, 0.5 + (flow_delta / 500.0) * 0.4)
                mechanism = "FORMATION_FLUID_INFLUX_MASS_IMBALANCE"
        elif dominant_hazard == "LOST_CIRCULATION":
            flow_delta = features.get("flow_delta_lpm", 0.0)
            if flow_delta < -100.0:
                physics_severity = min(1.0, 0.5 + (abs(flow_delta) / 500.0) * 0.4)
                mechanism = "HYDROSTATIC_FRACTURE_OR_DEPLETED_SAND_LOSS"
        elif dominant_hazard == "DIFFERENTIAL_STICKING":
            if features.get("rop", 10.0) < 1.0:
                physics_severity = 0.60
                mechanism = "MUD_CAKE_IMBEDDING_ACROSS_DEPLETED_SAND"

        # 3. If normal drilling is dominant (>0.60) and physics shows no hazard
        if ml_probs.get("normal", 0.0) > 0.65 and physics_severity < 0.2:
            dominant_hazard = "NORMAL_DRILLING"
            hazard_prob = 1.0 - ml_probs.get("normal", 0.0)
            mechanism = "STABLE_FORMATION_DRILLING"
        else:
            hazard_prob = dominant_prob

        # 4. Severity & lead time
        severity, lead_time = self.severity_calc.calculate_severity(
            ml_probability=hazard_prob,
            physics_severity=physics_severity,
            historical_offset_match=has_offset
        )

        # 5. Fused Confidence
        confidence = self.confidence_eval.calculate_fused_confidence(
            ml_probability=dominant_prob,
            physics_confirmed=physics_severity > 0.3,
            historical_citation_found=has_offset
        )

        # 6. Recommendations
        recommendations = self.rec_builder.build_recommendations(dominant_hazard, severity, formation)

        # 7. Formulate structured alert
        return self.alert_builder.create_alert(
            well_id=well_id,
            measured_depth=measured_depth,
            hazard_type=dominant_hazard,
            severity=severity,
            lead_time_seconds=lead_time,
            confidence_score=confidence,
            ml_probability=dominant_prob,
            physics_severity=physics_severity,
            mechanism=mechanism,
            recommendations=recommendations,
            citations=offset_evidence or []
        )
