"""A handover snapshot must survive Python/API process replacement, not just a reload."""

import json
import os
from pathlib import Path
import subprocess
import sys


def test_handover_survives_process_replacement(tmp_path):
    root = Path(__file__).resolve().parents[3]
    env = {**os.environ, "NWIS_DATA_DIR": str(tmp_path / "knowledge")}
    write = """
from apps.api.app.main import app
from apps.api.app.services.knowledge_store import list_events, save_decision
event = next(item for item in list_events() if item['well_id'] == 'MOR-118')
save_decision('NHK-421', event, 'Carry cited interval context into the next shift.', 'Demo reviewer', 'monitoring')
"""
    read = """
import json
from apps.api.app.main import app
from apps.api.app.services.knowledge_store import decisions_for
print(json.dumps(decisions_for('NHK-421')))
"""
    subprocess.run([sys.executable, "-c", write], cwd=root, env=env, check=True, timeout=30)
    result = subprocess.run([sys.executable, "-c", read], cwd=root, env=env, check=True,
                            timeout=30, text=True, capture_output=True)
    entries = json.loads(result.stdout)
    assert len(entries) == 1
    assert entries[0]["well_id"] == "NHK-421"
    assert entries[0]["source_snapshot"]["source_well_id"] == "MOR-118"
    assert "14.5 hours" in entries[0]["source_snapshot"]["excerpt"]
