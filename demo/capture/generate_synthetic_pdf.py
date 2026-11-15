"""Create a one-page, text-only synthetic NHK-412 source-review fixture."""

from pathlib import Path

OUTPUT = Path(__file__).resolve().parent / "fixtures" / "synthetic_nhk412_demo.pdf"
LINES = [
    "SYNTHETIC DEMONSTRATION RECORD - NOT FIELD DATA",
    "TRAINING-ONLY EXAMPLE - NOT AN OIL INDIA OPERATIONAL DOCUMENT",
    "",
    "WELL COMPLETION REPORT - SYNTHETIC REVIEW FIXTURE",
    "Well ID: NHK-412 (synthetic demo offset)",
    "Source ID: SYNTHETIC-NHK-412-REVIEW-DEMO",
    "Depth: 2912.0 m MD",
    "Stratigraphy: Barail Coal-Shale Formation",
    "Incident Type: SYNTHETIC DEMO - GAS KICK RESPONSE EXERCISE",
    "",
    "Description of Event:",
    "This fictional event exists only to demonstrate local PDF extraction,",
    "source review, and physical-page provenance in the NWIS prototype.",
    "No measurement or account on this page is an observed field record.",
    "",
    "Illustrative synthetic observations:",
    "A fictionalized 18 barrel pit gain was recorded over a short interval.",
    "A simulated flow check was performed for this training example.",
    "",
    "Recorded Response (synthetic example only):",
    "Mitigation: The crew followed a fictional shut-in and verification exercise.",
    "Outcome: synthetic scenario resolved for training demonstration.",
    "",
    "SOURCE PROVENANCE: generated synthetic PDF fixture for local capture.",
    "Page 1 is the physical page number of this generated PDF, not a",
    "physical OIL field report page. Do not use as operational guidance.",
    "SYNTHETIC DEMONSTRATION RECORD - NOT FIELD DATA",
]


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 10 Tf", "50 748 Td", "14 TL"]
    commands.extend(f"({_escape_pdf_text(line)}) Tj T*" for line in lines)
    commands.append("ET")
    stream = ("\n".join(commands) + "\n").encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
    ]
    result = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{index} 0 obj\n".encode("ascii"))
        result.extend(obj)
        result.extend(b"\nendobj\n")
    xref_offset = len(result)
    result.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    result.extend(b"0000000000 65535 f \n")
    result.extend(b"".join(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets[1:]))
    result.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return bytes(result)


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(build_pdf(LINES))
    print(OUTPUT)
