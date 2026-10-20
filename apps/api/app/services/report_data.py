"""Read structured facts and source excerpts from bundled synthetic WCR text."""

import re
import json
from pathlib import Path

REPORTS = Path(__file__).resolve().parents[4] / "data" / "synthetic" / "reports"
PROGNOSIS = REPORTS.parent / "formation_prognosis_nhk421.json"


def reports():
    return {p.stem.removeprefix("WCR_").replace("_", "-"): p for p in REPORTS.glob("WCR_*.txt")}


def formations(well_id: str):
    path = next((p for key, p in reports().items() if key.casefold() == well_id.casefold()), None)
    if path is None:
        if well_id.upper() == "NHK-421":
            prediction = json.loads(PROGNOSIS.read_text(encoding="utf-8"))
            return [{
                **interval,
                "tvd_top": None,
                "tvd_bottom": None,
                "primary_lithology": None,
                "hazard_warning": None,
                "depth_reference": "MD",
                "datum": prediction["datum"],
                "method": prediction["provenance"],
                "source_file": PROGNOSIS.name,
                "source_section": "formation_intervals",
            } for interval in prediction["formation_intervals"]]
        return None
    text = path.read_text(encoding="utf-8")
    section = re.search(r"(?ims)^\s*2\.\s*[^\n]*?(?:TOPS|SUCCESSION)[^\n]*\n(.*?)(?=^\s*\d+\.|\Z)", text)
    if not section:
        return []
    heading = next((line.strip() for line in section.group(0).splitlines() if line.strip()), "")
    result = []
    for line in section.group(1).splitlines():
        match = re.search(r"^\s*-\s*(.+?):\s*(?:Surface\s+to\s*|([\d,]+(?:\.\d+)?)\s*m\s*(?:to|-)\s*)([\d,]+(?:\.\d+)?)\s*m\s*MD\b", line, re.I)
        if not match:
            continue
        start = 0.0 if re.search(r"Surface", line, re.I) else float(match.group(2).replace(",", ""))
        result.append({
            "formation_name": match.group(1).strip(),
            "md_top": start,
            "tvd_top": None,
            "md_bottom": float(match.group(3).replace(",", "")),
            "tvd_bottom": None,
            "primary_lithology": None,
            "hazard_warning": None,
            "depth_reference": "MD",
            "datum": None,
            "method": "reported interval parsed from source text",
            "source_file": path.name,
            "source_section": heading,
        })
    return result


def events(well_id: str | None = None):
    found = []
    for key, path in reports().items():
        if well_id and key.casefold() != well_id.casefold():
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"(?im)^\s*Incident Type:\s*(.+)$", text):
            start = match.start()
            prior = list(re.finditer(r"(?im)^\s*\[PAGE\s+(\d+)\]\s*$", text[:start]))
            marker = prior[-1] if prior and start - prior[-1].end() < 1000 else None
            section_start = marker.start() if marker else start
            end = text.find("====", match.end())
            excerpt = text[section_start:end if end >= 0 else len(text)].strip()
            depth = re.search(r"(?i)(?:Depth:\s*)?([\d,]+(?:\.\d+)?)\s*m\s*MD\b", excerpt)
            formation = re.search(r"(?i)(?:Stratigraphy|Formation):\s*([^|\n]+)", excerpt)
            found.append({
                "event_id": f"{path.stem}:{match.start()}",
                "well_id": key,
                "event_type": match.group(1).strip(),
                "measured_depth_md_m": float(depth.group(1).replace(",", "")) if depth else None,
                "formation": formation.group(1).strip() if formation else None,
                "excerpt": excerpt,
                "source_file": path.name,
                "page_marker": int(marker.group(1)) if marker else None,
                "page_reference_type": "synthetic_text_report_marker_not_verified_pdf_page",
            })
    return found
