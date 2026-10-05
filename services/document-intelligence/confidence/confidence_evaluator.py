"""
StrataSentry-NWIS: Extraction Confidence Evaluator
Assigns statistical confidence to extracted entities based on OCR readability, unit validation, and stratigraphy.
"""

from typing import Dict, Any

class ExtractionConfidenceEvaluator:
    @staticmethod
    def evaluate_formation_confidence(extracted_top: Dict[str, Any]) -> float:
        score = 0.5
        # Top and bottom sanity
        if extracted_top.get("md_top", 0) < extracted_top.get("md_bottom", 99999):
            score += 0.25
        if extracted_top.get("formation_name"):
            score += 0.15
        if extracted_top.get("lithology") and extracted_top.get("lithology") != "Unspecified":
            score += 0.10
        return min(1.0, round(score, 2))

    @staticmethod
    def evaluate_incident_confidence(extracted_incident: Dict[str, Any]) -> float:
        score = 0.6
        if extracted_incident.get("categorized_type") != "UNKNOWN_INCIDENT":
            score += 0.3
        if extracted_incident.get("severity"):
            score += 0.1
        return min(1.0, round(score, 2))
