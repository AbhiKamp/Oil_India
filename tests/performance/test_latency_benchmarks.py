"""
StrataSentry-NWIS: Performance & Ingestion Latency Benchmarks
Verifies that processing latency is strictly well below the 500 ms real-time requirement.
"""

import time
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.services.orchestrator import DomainOrchestrator

def benchmark_telemetry_throughput(n_frames=500):
    orc = DomainOrchestrator()
    frame = {
        "well_id": "NHK-421",
        "measured_depth": 2845.0,
        "bit_depth": 2844.8,
        "rop": 14.0,
        "wob": 12.0,
        "surface_torque": 14.2,
        "rotary_rpm": 110,
        "standpipe_pressure": 2820.0,
        "flow_in": 2400.0,
        "flow_out_pct": 100.0,
        "pit_volume": 42.0,
        "mud_weight_in": 1.28,
        "ecd": 1.32,
        "gamma_ray": 85.0,
        "gas_total": 15.0
    }

    start = time.perf_counter()
    for _ in range(n_frames):
        orc.ingest_telemetry_frame(frame)
        orc.evaluate_live_risk("NHK-421")
    total_time = time.perf_counter() - start

    avg_ms = (total_time / n_frames) * 1000.0
    frames_per_sec = n_frames / total_time

    print("=" * 65)
    print("STRATASENTRY-NWIS REAL-TIME LATENCY BENCHMARK")
    print("=" * 65)
    print(f"Frames Ingested & Evaluated: {n_frames}")
    print(f"Total Wall Time:            {total_time:.3f} s")
    print(f"Average Frame Latency:      {avg_ms:.2f} ms (Target: < 500 ms)")
    print(f"Throughput Capacity:        {frames_per_sec:.1f} frames/sec")
    print("=" * 65)

    assert avg_ms < 500.0, f"Latency {avg_ms:.2f}ms exceeded 500ms budget!"

if __name__ == "__main__":
    benchmark_telemetry_throughput(500)
