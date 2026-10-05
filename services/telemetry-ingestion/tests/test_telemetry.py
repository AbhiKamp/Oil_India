import os
import sys
import pytest
import importlib.util

def load_mod(name, rel_path):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    full_path = os.path.join(base_dir, rel_path)
    spec = importlib.util.spec_from_file_location(name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

model_mod = load_mod("telemetry_model", "schemas/telemetry_model.py")
proc_mod = load_mod("stream_processor", "consumers/stream_processor.py")

def test_telemetry_schema_validation():
    packet = model_mod.DrillingTelemetryPacket(
        well_id="NHK-421",
        measured_depth=2845.2,
        bit_depth=2845.0,
        standpipe_pressure=3150.0,
        flow_in=2400.0,
        flow_out_pct=74.2,
        pit_volume=42.1
    )
    assert packet.well_id == "NHK-421"
    assert packet.measured_depth == 2845.2

def test_stream_processor_derivatives():
    processor = proc_mod.TelemetryStreamProcessor(window_size=30)
    for i in range(15):
        frame = {
            "standpipe_pressure": 2800.0 + i * 10.0, # rising SPP
            "surface_torque": 14.0 + (i % 3),
            "rop": 12.0,
            "wob": 10.0,
            "rotary_rpm": 100,
            "flow_in": 2400.0,
            "flow_out_pct": 75.0
        }
        enriched = processor.process_frame(frame)

    assert "spp_rate_of_change_psi_sec" in enriched
    assert enriched["spp_rate_of_change_psi_sec"] > 0.0 # Confirms positive slope
    assert "mse_ksi" in enriched
