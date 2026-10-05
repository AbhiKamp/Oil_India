"""
StrataSentry-NWIS: Drilling Event Extractor
Extracts drilling problems, stuck pipe, kicks, and lost circulation incidents.
"""

import re
from typing import List, Dict, Any

class EventExtractor:
    def __init__(self):
        self.hazard_keywords = {
            "STUCK_PIPE_PACKOFF": ["pack-off", "packoff", "hole pack", "sloughing coal", "tight hole on connection"],
            "STUCK_PIPE_DIFFERENTIAL": ["differential sticking", "differential stick", "stuck across sand", "filter cake"],
            "STUCK_PIPE_KEYSEAT": ["key seat", "keyseat", "dogleg ledge"],
            "GAS_KICK": ["gas kick", "kick", "pit gain", "flow check", "well flowing", "influx"],
            "LOST_CIRCULATION": ["lost circulation", "mud loss", "seepage loss", "pit volume drop", "depleted sand loss"]
        }

    def extract_events(self, text: str) -> List[Dict[str, Any]]:
        events = []
        # Look for Incident Type headers e.g.: 'Incident Type: MECHANICAL HOLE PACK-OFF & STUCK PIPE'
        inc_pattern = r'Incident Type:\s*([A-Za-z\s\-\/\&]+)'
        for m in re.finditer(inc_pattern, text, re.IGNORECASE):
            raw_type = m.group(1).strip()
            matched_category = "UNKNOWN_INCIDENT"
            for cat, kws in self.hazard_keywords.items():
                if any(kw in raw_type.lower() for kw in kws):
                    matched_category = cat
                    break

            events.append({
                "raw_incident_string": raw_type,
                "categorized_type": matched_category,
                "severity": "CRITICAL" if "STUCK" in matched_category or "KICK" in matched_category else "HIGH"
            })
        return events
