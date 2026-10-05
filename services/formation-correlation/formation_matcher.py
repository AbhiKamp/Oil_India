"""
StrataSentry-NWIS: Formation Matcher
Predicts stratigraphic boundary entry depths ahead of the drill bit using correlated offset wells.
"""

from typing import List, Dict, Any

class FormationMatcher:
    @staticmethod
    def predict_formation_tops_ahead_of_bit(
        current_md: float,
        depth_shift_m: float,
        offset_tops: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Projects offset formation tops into the active well using computed structural shift.
        """
        predictions = []
        for top in offset_tops:
            predicted_md = top["md_top"] - depth_shift_m
            distance_to_boundary = predicted_md - current_md

            predictions.append({
                "formation_name": top["formation_name"],
                "predicted_entry_md": round(predicted_md, 1),
                "distance_to_boundary_m": round(distance_to_boundary, 1),
                "status": "AHEAD_OF_BIT" if distance_to_boundary > 0 else "PENETRATED",
                "primary_lithology": top.get("primary_lithology", "Unspecified"),
                "hazard_warning": "HIGH_PRESSURE_TRANSITION" if "Barail" in top["formation_name"] or "Kopili" in top["formation_name"] else "NORMAL"
            })

        return sorted(predictions, key=lambda x: x["predicted_entry_md"])
