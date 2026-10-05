"""
StrataSentry-NWIS: Decision Auditor
Cryptographically logs every hazard alert and driller intervention for post-well incident analysis.
"""

import json
import hashlib
from datetime import datetime

class DecisionAuditor:
    def __init__(self, audit_file_path: str = "monitoring/audit/decision_audit_trail.log"):
        self.audit_path = audit_file_path
        self.last_hash = "0" * 64

    def log_decision(self, alert_data: dict, driller_ack: str = "PENDING"):
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "alert_id": alert_data.get("alert_id"),
            "well_id": alert_data.get("well_id"),
            "measured_depth": alert_data.get("measured_depth"),
            "hazard_type": alert_data.get("alert_type"),
            "severity": alert_data.get("severity"),
            "driller_ack": driller_ack,
            "prev_hash": self.last_hash
        }
        # Merkle chaining
        record_str = json.dumps(record, sort_keys=True)
        record_hash = hashlib.sha256(record_str.encode('utf-8')).hexdigest()
        record["hash"] = record_hash
        self.last_hash = record_hash

        try:
            with open(self.audit_path, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

        return record
