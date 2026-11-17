"""Replay a labeled synthetic drilling scenario into the local API."""

import argparse
import random
import time
from datetime import datetime, timedelta, timezone

import requests


def frames(well_id: str, rate_hz: float, incident: str, steps: int, seed: int = 26121):
    """Generate repeatable samples; step 20 is the start of the injected trend."""
    if rate_hz <= 0 or steps < 0:
        raise ValueError("rate_hz must be positive and steps cannot be negative")
    rng = random.Random(seed)
    md = 2845.0
    started = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
    step = 0
    while steps == 0 or step < steps:
        step += 1
        factor = min(1.0, max(0.0, (step - 20) / 30.0))
        rop = 14.0 + rng.uniform(-0.4, 0.4)
        spp = 2820.0 + rng.uniform(-15, 15)
        torque = 14.2 + rng.uniform(-0.5, 0.5)
        flow_out = 100.0 + rng.uniform(-0.5, 0.5)
        pit = 42.0
        ecd = 1.32 + rng.uniform(-0.005, 0.005)
        if incident == "packoff":
            rop = max(1.5, rop - factor * 11)
            spp += factor * 700
            torque += factor * 8 + (rng.uniform(-factor * 3, factor * 3) if factor else 0)
            flow_out -= factor * 25
            ecd += factor * 0.08
        elif incident == "kick":
            rop += factor * 12
            spp -= factor * 150
            flow_out += factor * 20
            pit += factor * 0.4
            ecd -= factor * 0.05

        md += rop / (3600 * rate_hz)
        yield {
            "timestamp": (started + timedelta(seconds=(step - 1) / rate_hz)).isoformat(),
            "well_id": well_id,
            "measured_depth": round(md, 3),
            "bit_depth": round(md - 0.2, 3),
            "rop": round(rop, 2),
            "wob": round(12.0 + rng.uniform(-0.3, 0.3), 2),
            "surface_torque": round(torque, 2),
            "rotary_rpm": 110 if rop > 3 else 70,
            "standpipe_pressure": round(spp, 1),
            "flow_in": 2400.0,
            "flow_out_pct": round(flow_out, 1),
            "pit_volume": round(pit, 2),
            "mud_weight_in": 1.28,
            "ecd": round(ecd, 3),
            "gamma_ray": round(85.0 + rng.uniform(-2, 2), 1),
            "gas_total": 18.5,
        }


def simulate(well_id: str, rate_hz: float, incident: str, api_url: str, steps: int, seed: int, no_delay: bool, reset: bool):
    print(f"SYNTHETIC REPLAY: {well_id} | {incident} | {rate_hz:g} samples/s")
    with requests.Session() as session:
        if reset:
            response = session.post(f"{api_url.rstrip('/')}/api/v1/demo/reset", timeout=5)
            response.raise_for_status()
        for index, packet in enumerate(frames(well_id, rate_hz, incident, steps, seed), start=1):
            response = session.post(
                f"{api_url.rstrip('/')}/api/v1/telemetry/{well_id}/ingest", json=packet, timeout=5
            )
            response.raise_for_status()
            print(f"{index:03d} | {packet['measured_depth']:.3f} m MD | "
                  f"SPP {packet['standpipe_pressure']:.0f} psi | ROP {packet['rop']:.1f} m/h")
            if not no_delay:
                time.sleep(1 / rate_hz)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream a synthetic telemetry replay")
    parser.add_argument("--well", default="NHK-421")
    parser.add_argument("--rate-hz", type=float, default=2.0)
    parser.add_argument("--inject-incident", choices=["none", "packoff", "kick"], default="none")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--steps", type=int, default=0, help="0 replays indefinitely")
    parser.add_argument("--seed", type=int, default=26121)
    parser.add_argument("--no-delay", action="store_true")
    parser.add_argument("--reset", action="store_true", help="reset all synthetic in-memory telemetry before replay")
    args = parser.parse_args()
    simulate(args.well, args.rate_hz, args.inject_incident, args.api_url, args.steps, args.seed, args.no_delay, args.reset)
