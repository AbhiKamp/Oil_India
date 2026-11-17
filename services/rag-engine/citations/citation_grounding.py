"""
Source attribution for the extractive evidence summary.
An exact excerpt match verifies attribution, not the scientific truth of a source.
"""

from typing import List, Dict, Any
import re

class CitationGroundingVerifier:
    @staticmethod
    def extract_and_verify_citations(llm_response: str, evidence_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parses citations and attaches verified source metadata.
        """
        citations = []
        for chunk in evidence_chunks:
            well_name = chunk.get("well_name")
            excerpt = (chunk.get("text") or "").strip()
            if well_name and excerpt and well_name.casefold() in llm_response.casefold() and excerpt in llm_response:
                citations.append({
                    "well_name": well_name,
                    "formation": chunk.get("formation_name"),
                    "md_top": chunk.get("md_top"),
                    "md_bottom": chunk.get("md_bottom"),
                    "document_name": chunk.get("document_name"),
                    "chunk_id": chunk.get("chunk_id"),
                    "page_number": chunk.get("page_number"),
                    "page_reference": chunk.get("page_number"),
                    "page_reference_type": chunk.get("page_reference_type"),
                    "verification": "exact_retrieved_excerpt_present_not_independent_fact_validation",
                })

        return citations
