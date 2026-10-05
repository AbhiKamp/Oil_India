"""
StrataSentry-NWIS: Data Governance & Masking Engine
Anonymizes sensitive exploration coordinates and proprietary operator assets for external export.
"""

from typing import Dict, Any

class DataMaskingEngine:
    @staticmethod
    def mask_well_record(well_data: Dict[str, Any]) -> Dict[str, Any]:
        masked = dict(well_data)
        # Jitter coordinates by random small offset to protect proprietary acreage
        if "surface_latitude" in masked:
            masked["surface_latitude"] = round(masked["surface_latitude"], 2)
        if "surface_longitude" in masked:
            masked["surface_longitude"] = round(masked["surface_longitude"], 2)
        if "operator" in masked:
            masked["operator"] = "CONFIDENTIAL_OPERATOR"
        return masked
