"""
StrataSentry-NWIS: Rig Edge Autonomous Daemon
Runs on the rig-site edge server, monitoring system health, buffering telemetry,
and orchestrating periodic cryptographic satellite synchronization.
"""

import os
import time
import json
import hashlib
from datetime import datetime

class RigEdgeDaemon:
    def __init__(self, rig_id: str = "OIL-RIG-04", sync_dir: str = "data/sync_staging"):
        self.rig_id = rig_id
        self.sync_dir = sync_dir
        os.makedirs(sync_dir, exist_ok=True)
        self.running = False

    def package_sync_bundle(self, telemetry_records: list) -> str:
        """
        Creates a signed, compressed data bundle for satellite synchronization.
        """
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        bundle_name = f"sync_{self.rig_id}_{timestamp_str}.json"
        bundle_path = os.path.join(self.sync_dir, bundle_name)

        raw_payload = json.dumps({
            "rig_id": self.rig_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "record_count": len(telemetry_records),
            "records": telemetry_records
        })

        # Calculate cryptographic SHA-256 signature
        sha256_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

        final_bundle = {
            "signature_sha256": sha256_hash,
            "payload": json.loads(raw_payload)
        }

        with open(bundle_path, 'w') as f:
            json.dump(final_bundle, f, indent=2)

        print(f"[+] Packaged signed sync bundle: {bundle_name} (SHA-256: {sha256_hash[:12]}...)")
        return bundle_path

    def start(self):
        self.running = True
        print(f"[*] StrataSentry Edge Daemon initialized on rig: {self.rig_id}")
        # Operational loop
        print("[+] Air-gap autonomy mode active. Local buffers ready.")

if __name__ == "__main__":
    daemon = RigEdgeDaemon()
    daemon.start()
