"""
StrataSentry-NWIS: WITSML 1.4.1.1 / 2.0 XML Parser
Parses WITSML standard wellLog and real-time drill-stream XML payloads.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from datetime import datetime

class WITSMLParser:
    @staticmethod
    def parse_log_data(xml_content: str) -> Dict[str, Any]:
        """
        Parses WITSML log XML and extracts mnemonic values.
        """
        try:
            root = ET.fromstring(xml_content)
            # Remove namespaces for straightforward xpathing
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]

            well_name = root.findtext(".//nameWell") or "UNKNOWN_WELL"
            data_str = root.findtext(".//data") or ""
            
            records = []
            if data_str:
                for line in data_str.strip().split("\n"):
                    parts = [p.strip() for p in line.split(",") if p.strip()]
                    if parts:
                        records.append(parts)

            return {
                "well_name": well_name,
                "record_count": len(records),
                "raw_records": records
            }
        except Exception as e:
            return {"error": f"Failed to parse WITSML XML: {str(e)}"}
