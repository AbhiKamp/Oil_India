"""
StrataSentry-NWIS: Well Name Canonicalization
Resolves disparate oilfield well naming formats into standardized canonical identifiers.
"""

import re

class WellNameNormalizer:
    @staticmethod
    def canonicalize(raw_name: str) -> str:
        """
        Examples:
        'Nahorkatiya #421' -> 'NHK-421'
        'Nahorkatiya-421' -> 'NHK-421'
        'NHK 421' -> 'NHK-421'
        'Moran Well 118' -> 'MOR-118'
        'Baghjan #07' -> 'BGH-07'
        'Digboi-02' -> 'DGB-02'
        """
        name = raw_name.strip().upper()
        # Nahorkatiya mappings
        if "NAHORKATIYA" in name or "NHK" in name:
            num = re.search(r'\d+', name)
            return f"NHK-{num.group(0)}" if num else "NHK-UNKNOWN"
        # Moran mappings
        if "MORAN" in name or "MOR" in name:
            num = re.search(r'\d+', name)
            return f"MOR-{num.group(0)}" if num else "MOR-UNKNOWN"
        # Baghjan mappings
        if "BAGHJAN" in name or "BGH" in name:
            num = re.search(r'\d+', name)
            return f"BGH-{num.group(0).zfill(2)}" if num else "BGH-UNKNOWN"
        # Digboi mappings
        if "DIGBOI" in name or "DGB" in name:
            num = re.search(r'\d+', name)
            return f"DGB-{num.group(0).zfill(2)}" if num else "DGB-UNKNOWN"

        # Generic cleanup: replace spaces and hashes with hyphens
        cleaned = re.sub(r'[\s\#]+', '-', name)
        return cleaned
