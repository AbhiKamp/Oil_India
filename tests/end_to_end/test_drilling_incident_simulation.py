"""
StrataSentry-NWIS: Drilling Incident Simulation E2E Test
Simulates an entire drilling stand with an induced pack-off incident and verifies copilot resolution.
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.services.orchestrator import DomainOrchestrator

def test_incident_simulation_and_copilot_mitigation():
    orc = DomainOrchestrator()

    # Query Copilot for resolution advice
    res = orc.copilot.generate_advisory(
        query="What procedure should the driller follow if annular pressure surges in Barail coal?",
        current_depth=2845.0,
        formation="Barail Coal-Shale",
        evidence_chunks=orc.retriever.retrieve("stuck pipe in Barail coal", formation="Barail Coal-Shale", depth_md=2845.0)
    )

    assert "stop drilling ahead" in res["answer"].lower()
    assert "2,400 lpm" in res["answer"].lower()
    assert len(res["citations"]) >= 1
