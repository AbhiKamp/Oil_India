"""
StrataSentry-NWIS: Document Intelligence - PDF Parser
Extracts clean structured text and layout sections from Well Completion Reports (WCR).
"""

import os
import re
from typing import Dict, List, Any

class PDFParser:
    def __init__(self):
        self.supported_extensions = ['.pdf', '.txt']

    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parses document content, extracting sections and metadata.
        Falls back smoothly to text reading if pypdf/fitz is not installed or for plain text WCRs.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found at: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        pages = []

        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            pages.append({"page_number": 1, "text": content})
        elif ext == '.pdf':
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    pages.append({"page_number": i + 1, "text": page.extract_text() or ""})
            except ImportError:
                # Basic binary string extraction fallback
                with open(file_path, 'rb') as f:
                    raw = f.read()
                # Extract ASCII text strings
                strings = re.findall(b"[\x20-\x7E]{4,}", raw)
                decoded = "\n".join(s.decode('latin1') for s in strings)
                pages.append({"page_number": 1, "text": decoded})

        sections = self._split_into_sections(pages)
        return {
            "file_name": os.path.basename(file_path),
            "total_pages": len(pages),
            "pages": pages,
            "sections": sections
        }

    def _split_into_sections(self, pages: List[Dict[str, Any]]) -> Dict[str, str]:
        sections = {}
        current_section = "GENERAL"
        buffer = []

        section_headers = [
            "GENERAL WELL INFORMATION",
            "STRATIGRAPHIC SUCCESSION",
            "CASING & MUD PROGRAM",
            "DRILLING PROBLEMS & INCIDENT LOG",
            "LOGGING & WIRELINE EVALUATION",
            "RECOMMENDATIONS"
        ]

        for p in pages:
            lines = p["text"].split("\n")
            for line in lines:
                matched_header = None
                for sh in section_headers:
                    if sh in line.upper():
                        matched_header = sh
                        break
                if matched_header:
                    if buffer:
                        sections[current_section] = "\n".join(buffer).strip()
                        buffer = []
                    current_section = matched_header
                buffer.append(line)

        if buffer:
            sections[current_section] = "\n".join(buffer).strip()

        return sections
