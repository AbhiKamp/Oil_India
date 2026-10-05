"""
StrataSentry-NWIS: Depth Extractor
Extracts Measured Depth (MD) and True Vertical Depth (TVD) intervals from unstructured text.
"""

import re
from typing import List, Dict, Any, Optional

class DepthExtractor:
    def __init__(self):
        # Patterns for MD and TVD
        self.depth_patterns = [
            r'Depth:\s*([\d,]+(?:\.\d+)?)\s*m\s*(?:MD)?(?:\s*\(([\d,]+(?:\.\d+)?)\s*m\s*TVD\))?',
            r'at\s+([\d,]+(?:\.\d+)?)\s*m\s*MD',
            r'from\s+([\d,]+(?:\.\d+)?)\s*(?:m)?\s+to\s+([\d,]+(?:\.\d+)?)\s*m\s*MD'
        ]

    def extract_depths(self, text: str) -> List[Dict[str, Any]]:
        results = []
        # Check single depth or MD/TVD pair
        p1 = r'Depth:\s*([\d,]+(?:\.\d+)?)\s*m\s*(?:MD)?(?:\s*\(([\d,]+(?:\.\d+)?)\s*m\s*TVD\))?'
        for match in re.finditer(p1, text, re.IGNORECASE):
            md_str, tvd_str = match.groups()
            md = float(md_str.replace(',', ''))
            tvd = float(tvd_str.replace(',', '')) if tvd_str else None
            results.append({"type": "point", "md": md, "tvd": tvd})

        # Check intervals: '2,835 m and 2,852 m MD' or 'from X to Y'
        p2 = r'(?:between|from)\s+([\d,]+(?:\.\d+)?)\s*m?\s+(?:and|to)\s+([\d,]+(?:\.\d+)?)\s*m\s*MD'
        for match in re.finditer(p2, text, re.IGNORECASE):
            top_str, btm_str = match.groups()
            results.append({
                "type": "interval",
                "md_top": float(top_str.replace(',', '')),
                "md_bottom": float(btm_str.replace(',', ''))
            })

        return results
