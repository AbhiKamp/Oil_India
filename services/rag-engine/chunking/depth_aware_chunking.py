"""
StrataSentry-NWIS: Depth-Aware Semantic Chunker
Splits Well Completion Reports and Mudlogs into depth-anchored stratigraphic chunks.
"""

from typing import List, Dict, Any
import re

class DepthAwareChunker:
    def __init__(self, max_depth_span_m: float = 30.0):
        self.max_depth_span = max_depth_span_m

    def chunk_wcr_document(
        self,
        document_text: str,
        well_name: str,
        default_formation: str = "Barail Coal-Shale"
    ) -> List[Dict[str, Any]]:
        """
        Parses text and creates semantic chunks preserving well_name, depth interval, formation, and page references.
        """
        chunks = []
        # Split on section marks or page markers
        pages = re.split(r'\[PAGE\s+(\d+)\]', document_text)
        
        current_page = 1
        i = 0
        while i < len(pages):
            part = pages[i]
            if part.isdigit():
                current_page = int(part)
                i += 1
                if i < len(pages):
                    part = pages[i]
                else:
                    break

            # Extract depth mentions
            depth_matches = re.findall(r'([\d,]+(?:\.\d+)?)\s*m\s*MD', part)
            if depth_matches:
                depth_floats = [float(d.replace(',', '')) for d in depth_matches]
                md_top = min(depth_floats)
                md_bottom = max(depth_floats)
            else:
                md_top = None
                md_bottom = None

            # Detect formation mentioned
            formation = default_formation
            for f_name in ["Dihing", "Tipam", "Girujan", "Barail", "Kopili", "Sylhet"]:
                if f_name.lower() in part.lower():
                    formation = f"{f_name} Formation"
                    break

            if len(part.strip()) > 50:
                chunks.append({
                    "chunk_id": f"{well_name}_p{current_page}_c{len(chunks)}",
                    "well_name": well_name,
                    "page_number": current_page,
                    "formation_name": formation,
                    "md_top": md_top,
                    "md_bottom": md_bottom,
                    "text": part.strip(),
                    "has_incident": any(w in part.lower() for w in ["stuck", "pack-off", "kick", "lost circulation", "caving"])
                })
            i += 1

        return chunks
