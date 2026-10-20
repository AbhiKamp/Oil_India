"""Small contract check for deterministic synthetic telemetry."""

import importlib.util
from pathlib import Path


def test_replay_is_repeatable_and_baseline_has_no_artificial_loss():
    path = Path(__file__).resolve().parents[1] / "scripts" / "simulate_telemetry.py"
    spec = importlib.util.spec_from_file_location("simulate_telemetry", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    normal = list(module.frames("NHK-421", 2, "none", 50))
    assert normal == list(module.frames("NHK-421", 2, "none", 50))
    assert all(99 <= frame["flow_out_pct"] <= 101 for frame in normal)
    packoff = list(module.frames("NHK-421", 2, "packoff", 50))
    kick = list(module.frames("NHK-421", 2, "kick", 50))
    assert packoff[0] == normal[0] == kick[0]
    assert packoff[-1]["standpipe_pressure"] > normal[-1]["standpipe_pressure"]
    assert packoff[-1]["flow_out_pct"] < normal[-1]["flow_out_pct"]
    assert kick[-1]["pit_volume"] > normal[-1]["pit_volume"]
    assert kick[-1]["flow_out_pct"] > normal[-1]["flow_out_pct"]
