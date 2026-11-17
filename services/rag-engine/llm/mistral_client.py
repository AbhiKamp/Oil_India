"""
Compatibility wrapper for the local extractive evidence summary.
No language model, remote provider, or operational advisory is implemented here.
"""

import os
from typing import Dict, Any, List
try:
    from ..citations.citation_grounding import CitationGroundingVerifier
except (ImportError, ValueError):
    from citations.citation_grounding import CitationGroundingVerifier

class MistralDrillingCopilot:
    def __init__(self, provider: str = None, api_key: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "offline_mock")
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY", "")
        self.verifier = CitationGroundingVerifier()

    def generate_advisory(
        self,
        query: str,
        current_depth: float,
        formation: str,
        evidence_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Return an evidence-bound summary, or abstain when evidence is absent."""
        # No model provider is implemented in this evidence-only local mode.
        answer = self._generate_offline_grounded_response(query, current_depth, formation, evidence_chunks)
        citations = self.verifier.extract_and_verify_citations(answer, evidence_chunks)

        return {
            "answer": answer,
            "citations": citations,
            "evidence_count": len(evidence_chunks),
            "engine": "local_evidence_summary_no_language_model"
        }

    def _generate_offline_grounded_response(
        self,
        query: str,
        current_depth: float,
        formation: str,
        evidence: List[Dict[str, Any]]
    ) -> str:
        if not evidence:
            return "Insufficient retrieved evidence to answer this question. No source or operational outcome is asserted."

        excerpts = []
        for record in evidence:
            well = record.get("well_name") or "Unidentified well"
            page = record.get("page_number")
            kind = record.get("page_reference_type")
            label = "PDF page" if kind == "physical_pdf_page" else "text marker"
            location = f", {label} {page}" if page is not None else ""
            text = record.get("text", "").strip()
            if text:
                excerpts.append(f"Retrieved record ({well}{location}): {text}")
        if not excerpts:
            return "Insufficient source text in the retrieved evidence to answer this question."
        return (
            "Retrieved historical evidence for review:\n" + "\n".join(excerpts) +
            "\n\nThese records describe reported history only; they do not establish a current cause, "
            "successful outcome, or appropriate operating action. No setpoint or procedure is prescribed."
        )
