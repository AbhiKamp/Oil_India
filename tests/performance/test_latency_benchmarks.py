"""
Local in-process compute timing on the tiny synthetic corpus.
Excludes HTTP, sensors, ingestion queues, and browser presentation; not a capacity claim.
"""

import time
import os
import sys
import statistics

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

    timings = []
    start = time.perf_counter()
    for _ in range(n_frames):
        before = time.perf_counter()
        orc.ingest_telemetry_frame(frame)
        orc.evaluate_live_risk("NHK-421")
        timings.append((time.perf_counter() - before) * 1000.0)
    total_time = time.perf_counter() - start

    avg_ms = (total_time / n_frames) * 1000.0
    p95_ms = sorted(timings)[min(n_frames - 1, int(n_frames * .95))]

    print("=" * 65)
    print("NWIS LOCAL SYNTHETIC COMPUTE BENCHMARK (NOT END-TO-END)")
    print("=" * 65)
    print(f"Frames Ingested & Evaluated: {n_frames}")
    print(f"Total Wall Time:            {total_time:.3f} s")
    print(f"Average Compute Latency:    {avg_ms:.2f} ms")
    print(f"Median / p95 Compute:       {statistics.median(timings):.2f} / {p95_ms:.2f} ms")
    print("Excludes transport and UI; repeated synthetic input only.")
    print("=" * 65)

    return {"frames": n_frames, "average_ms": avg_ms, "p95_ms": p95_ms}

if __name__ == "__main__":
    benchmark_telemetry_throughput(500)
