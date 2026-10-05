"""
StrataSentry-NWIS: Immutable Security Audit Trail
"""

import hashlib
import json
from datetime import datetime

class SecurityAuditTrail:
    @staticmethod
    def create_security_event(user_id: str, action: str, resource: str, success: bool = True) -> dict:
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "success": success
        }
        event["event_hash"] = hashlib.sha256(json.dumps(event).encode('utf-8')).hexdigest()
        return event
