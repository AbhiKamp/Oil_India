"""
StrataSentry-NWIS: Real-Time Telemetry Rig Simulator
Streams high-frequency MWD/LWD drilling sensor packets into the platform gateway.
"""

import time
import argparse
import requests
import json
import random
from datetime import datetime

def simulate(well_id: str, rate_hz: float, incident: str, api_url: str):
    print("=" * 65)
    print(f"STREAMING LIVE DRILLING TELEMETRY -> {well_id}")
    print(f"Sampling Frequency: {rate_hz} Hz | Injected Incident: {incident.upper()}")
    print(f"Gateway Destination: {api_url}")
    print("=" * 65)

    md = 2845.0
    bit_depth = 2844.8
    step = 0

    while True:
        step += 1
        # Baseline parameters
        if incident == "packoff" and step > 20:
            factor = min(1.0, (step - 20) / 30.0)
            rop = max(1.5, 14.0 - factor * 11.0)
            spp = 2820.0 + factor * 700.0 + random.uniform(-15, 15)
            torque = 14.5 + factor * 8.0 + random.uniform(-3, 3)
            flow_out = 75.0 - factor * 8.0
            ecd = 1.32 + factor * 0.08
            gr = 95.0 + factor * 20.0
        elif incident == "kick" and step > 20:
            factor = min(1.0, (step - 20) / 25.0)
            rop = 14.0 + factor * 12.0 # Drilling break
            spp = 2820.0 - factor * 150.0
            torque = 14.0 + random.uniform(-0.5, 0.5)
            flow_out = 75.0 + factor * 22.0 # Flow out increases
            ecd = 1.32 - factor * 0.05
            gr = 85.0
        else:
            rop = 14.0 + random.uniform(-0.4, 0.4)
            spp = 2820.0 + random.uniform(-15, 15)
            torque = 14.2 + random.uniform(-0.5, 0.5)
            flow_out = 75.0 + random.uniform(-0.5, 0.5)
            ecd = 1.32 + random.uniform(-0.005, 0.005)
            gr = 85.0 + random.uniform(-2, 2)

        md += (rop / 3600.0) / rate_hz
        bit_depth = md - 0.2

        packet = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "well_id": well_id,
            "measured_depth": round(md, 3),
            "bit_depth": round(bit_depth, 3),
            "rop": round(rop, 2),
            "wob": round(12.0 + random.uniform(-0.3, 0.3), 2),
            "surface_torque": round(torque, 2),
            "rotary_rpm": 110 if rop > 3 else 70,
            "standpipe_pressure": round(spp, 1),
            "flow_in": 2400.0,
            "flow_out_pct": round(flow_out, 1),
            "pit_volume": round(42.0 + (0.4 if incident == 'kick' else 0.0), 2),
            "mud_weight_in": 1.28,
            "ecd": round(ecd, 3),
            "gamma_ray": round(gr, 1),
            "gas_total": 18.5
        }

        # Dispatch to API
        try:
            requests.post(f"{api_url}/api/v1/telemetry/{well_id}/ingest", json=packet, timeout=1.0)
            status_symbol = "⚠️ PACKOFF" if incident == 'packoff' and step > 25 else "🟢 NOMINAL"
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Depth: {md:.2f}m | SPP: {spp:.0f} psi | ROP: {rop:.1f} m/h | Torque: {torque:.1f} kNm | {status_symbol}")
        except Exception:
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Local packet buffered: Depth {md:.2f}m")

        time.sleep(1.0 / rate_hz)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StrataSentry Telemetry Simulator")
    parser.add_argument("--well", default="NHK-421", help="Target well ID")
    parser.add_argument("--rate-hz", type=float, default=1.0, help="Transmission rate in Hz")
    parser.add_argument("--inject-incident", choices=["none", "packoff", "kick", "loss"], default="none")
    parser.add_argument("--api-url", default="http://localhost:8000", help="FastAPI gateway base URL")
    args = parser.parse_args()

    simulate(args.well, args.rate_hz, args.inject_incident, args.api_url)
