"""
StrataSentry-NWIS: Historical Well Log & Telemetry Replay Engine
Replays historical well runs through the analytics engine to evaluate lead-time and accuracy.
"""

import os
import sys
import pandas as pd
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.services.orchestrator import DomainOrchestrator

def replay_historical_dataset(csv_file_path: str):
    if not os.path.exists(csv_file_path):
        print(f"[!] File not found: {csv_file_path}")
        return

    print("=" * 65)
    print(f"REPLAYING HISTORICAL TELEMETRY: {os.path.basename(csv_file_path)}")
    print("=" * 65)

    df = pd.read_csv(csv_file_path)
    orc = DomainOrchestrator()

    alert_count = 0
    first_warning_depth = None

    for idx, row in df.iterrows():
        frame = row.to_dict()
        orc.ingest_telemetry_frame(frame)
        alert = orc.evaluate_live_risk(frame.get("well_id", "NHK-421"))

        if alert.get("severity") in ["WARNING", "CRITICAL"]:
            alert_count += 1
            if first_warning_depth is None:
                first_warning_depth = frame.get("measured_depth")
                print(f"[!] >>> FIRST HAZARD EARLY WARNING DISPATCHED AT DEPTH: {first_warning_depth}m MD <<<")
                print(f"    Hazard: {alert.get('alert_type')} | Confidence: {alert.get('confidence_score') * 100:.0f}%")
                print(f"    Action: {alert.get('driller_action_summary')}")

    print("=" * 65)
    print(f"Replay Complete. Total frames: {len(df)} | Warnings triggered: {alert_count}")
    print(f"Earliest Detection Depth: {first_warning_depth}m MD")
    print("=" * 65)

if __name__ == "__main__":
    path = os.path.join(PROJECT_ROOT, "data", "synthetic", "telemetry", "telemetry_packoff_incident.csv")
    replay_historical_dataset(path)
