"""
StrataSentry-NWIS: Qdrant Metadata Filter Builder
Constructs strict formation, depth, and hazard payload filters for Qdrant vector retrieval.
"""

from typing import Dict, Any, Optional

class MetadataFilterBuilder:
    @staticmethod
    def build_qdrant_filter(
        formation_name: Optional[str] = None,
        depth_md: Optional[float] = None,
        depth_tolerance_m: float = 100.0,
        incident_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds Qdrant JSON filter object.
        """
        must_clauses = []

        if formation_name:
            must_clauses.append({
                "key": "formation_name",
                "match": { "value": formation_name }
            })

        if incident_type:
            must_clauses.append({
                "key": "incident_type",
                "match": { "value": incident_type }
            })

        if depth_md is not None:
            must_clauses.append({
                "key": "md_top",
                "range": {
                    "gte": max(0.0, depth_md - depth_tolerance_m),
                    "lte": depth_md + depth_tolerance_m
                }
            })

        return { "must": must_clauses } if must_clauses else {}
