"""
StrataSentry-NWIS: Formation Extractor
Identifies stratigraphic formations and boundaries from unstructured reports.
"""

import re
from typing import List, Dict, Any

KNOWN_FORMATIONS = [
    "Dihing Formation",
    "Dhekiajuli Formation",
    "Tipam Sandstone",
    "Girujan Clay",
    "Barail Coal-Shale",
    "Barail Formation",
    "Barail Main Sand",
    "Kopili Formation",
    "Sylhet Limestone",
    "Disang Group"
]

class FormationExtractor:
    def extract_formation_tops(self, text: str) -> List[Dict[str, Any]]:
        tops = []
        # Pattern e.g.: '- Tipam Sandstone: 610 m to 1,820 m MD (Massive porous water sands)'
        pattern = r'-\s*([A-Za-z\s\-]+):\s*([\d,]+(?:\.\d+)?)\s*m\s+to\s+([\d,]+(?:\.\d+)?)\s*m\s*MD\s*(?:\((.*?)\))?'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            name, top, btm, desc = m.groups()
            name_clean = name.strip()
            # Normalize against known formations
            for kf in KNOWN_FORMATIONS:
                if kf.lower() in name_clean.lower() or name_clean.lower() in kf.lower():
                    name_clean = kf
                    break

            tops.append({
                "formation_name": name_clean,
                "md_top": float(top.replace(',', '')),
                "md_bottom": float(btm.replace(',', '')),
                "lithology": desc.strip() if desc else "Unspecified"
            })
        return tops
