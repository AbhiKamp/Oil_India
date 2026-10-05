"""
StrataSentry-NWIS: Mitigation Extractor
Extracts fishing operations, jarring procedures, LCM pills, and well kill procedures.
"""

import re
from typing import List, Dict, Any

class MitigationExtractor:
    def extract_mitigation_actions(self, text: str) -> List[Dict[str, Any]]:
        mitigations = []
        # Match 'Mitigation Procedure & Fishing Actions Taken:' or 'Immediate Well Control Actions Taken:'
        pattern = r'(?:Mitigation Procedure|Actions Taken|Fishing Actions|Well Control Actions)(?:.*?):(.*?)(?:Recommendations|Total NPT|\={4,}|\Z)'
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        for m in matches:
            body = m.group(1).strip()
            # Split numbered items
            steps = [s.strip() for s in re.split(r'\n\s*\d+\.\s*', body) if s.strip()]
            mitigations.append({
                "raw_text": body,
                "steps": steps
            })
        return mitigations
