"""
StrataSentry-NWIS: Document Intelligence - Tabular Parser
Extracts casing schedules, mud programs, and survey tables from report text.
"""

import re
from typing import List, Dict, Any

class TableParser:
    def extract_casing_table(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts casing sizes, setting depths, and mud weights.
        Example line: '9-5/8" Intermediate Casing set at 2,520.0 m MD (Mud Weight: 1.22 SG)'
        """
        casing_records = []
        pattern = r'(\d+[\-\/]?\d*\"?)\s+([A-Za-z\s]+Casing)\s+set\s+at\s+([\d,]+(?:\.\d+)?)\s*m.*?Mud Weight:\s*([\d\.]+)\s*SG'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            size, c_type, depth, mw = m.groups()
            casing_records.append({
                "casing_size": size.strip(),
                "casing_type": c_type.strip(),
                "setting_depth_md_m": float(depth.replace(',', '')),
                "mud_weight_sg": float(mw)
            })
        return casing_records

    def extract_survey_table(self, text: str) -> List[Dict[str, float]]:
        """
        Extracts MD, Inc, Azimuth rows.
        """
        surveys = []
        pattern = r'^\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)'
        for line in text.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                md, inc, azi = match.groups()
                surveys.append({
                    "measured_depth": float(md),
                    "inclination_deg": float(inc),
                    "azimuth_deg": float(azi)
                })
        return surveys
