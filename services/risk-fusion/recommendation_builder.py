"""Build evidence-review language for risk alerts."""

from typing import List

class DrillerRecommendationBuilder:
    @staticmethod
    def build_recommendations(hazard_type: str, severity: str, formation: str) -> List[str]:
        return [
            f"Review the {hazard_type.replace('_', ' ').lower()} assessment for {formation} against current measurements and source evidence.",
            "Consult the approved well programme and applicable site procedures with the responsible drilling or well-control personnel.",
            "No operating setpoints or mandatory actions are established by this heuristic assessment."
        ]
