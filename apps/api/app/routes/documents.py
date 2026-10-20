"""Bundled source reports and persistent local document ingestion."""

import hashlib
import io
import re
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from ..services import knowledge_store as store
from ..services.report_data import REPORTS, formations as source_formations, reports

router = APIRouter(prefix="/api/v1/documents", tags=["Documents & Knowledge"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 100
MAX_EXTRACTED_CHARS = 2_000_000
MAX_OCR_PAGES = 10
ALLOWED_EXTENSIONS = {"pdf", "txt"}


def _events_from_pages(pages: list[dict], well_id: str, source_file: str) -> list[dict]:
    found = []
    for page in pages:
        text = page["text"]
        matches = list(re.finditer(r"(?im)^\s*Incident Type:\s*(.+)$", text))
        for index, match in enumerate(matches):
            start = match.start()
            delimiter = re.search(r"(?m)^\s*(?:=+|\[PAGE\s+\d+\])\s*$", text[match.end():])
            next_incident = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            next_boundary = match.end() + delimiter.start() if delimiter else len(text)
            boundaries = (next_incident, next_boundary)
            excerpt_end = min(boundaries)
            excerpt_body = text[start:excerpt_end].strip()
            # Metadata is often directly above Incident Type. Walk only over adjacent
            # depth/formation lines so an earlier incident's details cannot bleed in.
            preceding = []
            for line in reversed(text[:start].splitlines()):
                if not line.strip():
                    if preceding:
                        preceding.append(line)
                    continue
                if re.search(r"(?i)(?:Depth:\s*)?[\d,]+(?:\.\d+)?\s*m\s*MD\b|(?:Stratigraphy|Formation):", line):
                    preceding.append(line)
                else:
                    break
            metadata = "\n".join(reversed(preceding))
            excerpt = (metadata + "\n" + excerpt_body).strip()
            depth = re.search(r"(?i)(?:Depth:\s*)?([\d,]+(?:\.\d+)?)\s*m\s*MD\b", metadata)
            depth = depth or re.search(r"(?i)(?:Depth:\s*)?([\d,]+(?:\.\d+)?)\s*m\s*MD\b", excerpt_body)
            formation = re.search(r"(?i)(?:Stratigraphy|Formation):\s*([^|\n]+)", metadata)
            formation = formation or re.search(r"(?i)(?:Stratigraphy|Formation):\s*([^|\n]+)", excerpt_body)
            found.append({
                "well_id": well_id, "event_type": match.group(1).strip(),
                "measured_depth_md_m": float(depth.group(1).replace(",", "")) if depth else None,
                "formation": formation.group(1).strip() if formation else None,
                "excerpt": excerpt, "source_file": source_file,
                "page_marker": page["page_number"],
                "page_reference_type": "physical_pdf_page" if page.get("physical") else "text_source_page",
                "extraction_method": page.get("extraction_method", "text"),
                "review_state": "needs_review", "mitigation": None, "outcome": None,
            })
    return found


@router.get("")
async def list_documents():
    bundled = [{"document_name": path.name, "well_name": path.stem.removeprefix("WCR_").replace("_", "-"),
                "type": "Synthetic text report", "source_format": "text", "status": "LOCAL_SOURCE",
                "physical_pdf_available": False}
               for path in sorted(REPORTS.glob("WCR_*.txt"))]
    uploads = [{"document_name": row["document_id"], "original_name": row["original_name"],
                "well_name": row["well_name"], "type": "Uploaded report", "source_format": row["source_format"],
                "status": row["status"], "physical_pdf_available": bool(row["physical_pdf_available"]),
                "document_id": row["document_id"], "provenance": row["provenance"]}
               for row in store.uploaded_documents()]
    return bundled + uploads


@router.post("")
async def upload_document(file: UploadFile = File(...), well_id: str = Form(...),
                          provenance: str = Form("synthetic")):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", well_id):
        raise HTTPException(422, "Invalid well_id")
    if provenance not in {"synthetic", "user_supplied"}:
        raise HTTPException(422, "provenance must be synthetic or user_supplied")
    name = re.sub(r"[\x00-\x1f\x7f]", "", Path(file.filename or "").name)[:255]
    extension = Path(name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, "Only PDF and TXT uploads are supported")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Upload exceeds 10 MiB limit")
    if not content:
        raise HTTPException(422, "Uploaded file is empty")
    if extension == "pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(422, "PDF signature is invalid")
    if extension == "txt":
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(422, "TXT must be UTF-8") from exc
        pages = [{"page_number": 1, "text": text}]
        parsed_status = "extracted"
    else:
        digest = hashlib.sha256(content).hexdigest()
        try:
            import pypdf
        except ImportError as exc:
            raise HTTPException(503, "PDF text extraction dependency is unavailable") from exc
        try:
            pages_text = await run_in_threadpool(_extract_pdf_text, pypdf, content)
        except ValueError as exc:
            raise HTTPException(413, str(exc)) from exc
        except Exception as exc:
            raise HTTPException(422, "PDF is malformed or cannot be read") from exc
        pages = [{"page_number": i + 1, "text": text, "physical": True,
                  "extraction_method": "pdf_text" if text.strip() else "needs_ocr"}
                 for i, text in enumerate(pages_text)]
        if not pages:
            raise HTTPException(422, "PDF contains no pages")
        parsed_status, extraction_detail = await _ocr_empty_pages(content, pages)
    # Stable content identity makes re-upload idempotent; stored paths never use client names.
    doc_id = f"upload-{hashlib.sha256(content).hexdigest()[:24]}"
    extracted = _events_from_pages(pages, well_id, doc_id)
    try:
        document, events, created = store.insert_upload(
            content=content, original_name=name or "upload." + extension, well_id=well_id,
            provenance=provenance, extension=extension, pages=pages, events=extracted, status=parsed_status)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(507, "Unable to persist uploaded document") from exc
    response_events = [{key: value for key, value in item.items() if key != "document_id"} for item in events]
    return {"document_id": document["document_id"], "document_name": document["document_id"],
            "original_name": document["original_name"], "well_name": document["well_name"],
            "provenance": document["provenance"], "source_format": document["source_format"],
            "status": document["status"], "physical_pdf_available": bool(document["physical_pdf_available"]),
            "content_hash": document["content_hash"], "deduplicated": not created,
            "extraction_status": extraction_detail if extension == "pdf" else "complete",
            "events": response_events}


def _extract_pdf_text(pypdf, content: bytes) -> list[str]:
    reader = pypdf.PdfReader(io.BytesIO(content), strict=True)
    if len(reader.pages) > MAX_PDF_PAGES:
        raise ValueError(f"PDF exceeds {MAX_PDF_PAGES} page limit")
    pages = []
    total_chars = 0
    for page in reader.pages:
        text = page.extract_text() or ""
        total_chars += len(text)
        if total_chars > MAX_EXTRACTED_CHARS:
            raise ValueError(f"PDF extracted text exceeds {MAX_EXTRACTED_CHARS} character limit")
        pages.append(text)
    return pages


async def _ocr_empty_pages(content: bytes, pages: list[dict]) -> tuple[str, str]:
    scanned = [page["page_number"] for page in pages if not page["text"].strip()]
    if not scanned:
        return "extracted", "complete"
    if len(scanned) > MAX_OCR_PAGES:
        return "needs_ocr", f"needs OCR (automatic limit is {MAX_OCR_PAGES} scanned pages)"
    from services.document_intelligence.parsers.ocr_parser import (
        OCRExecutionError, OCRLimitError, OCRUnavailableError,
    )
    try:
        result = await run_in_threadpool(_run_pdf_ocr, content, scanned)
    except OCRUnavailableError as exc:
        return "ocr_unavailable", str(exc)
    except OCRLimitError as exc:
        return "needs_ocr", str(exc)
    except OCRExecutionError as exc:
        return "ocr_failed", str(exc)
    for page in result["pages"]:
        target = pages[page["page_number"] - 1]
        target["text"] = page["text"]
        target["extraction_method"] = "ocr"
    if not any(page["text"].strip() for page in pages):
        return "needs_ocr", "needs OCR (no text was recognized)"
    return "extracted", "complete (OCR applied to scanned pages)"


def _run_pdf_ocr(content: bytes, page_numbers: list[int]) -> dict:
    import tempfile
    from pathlib import Path
    from services.document_intelligence.parsers.ocr_parser import OCRParser

    with tempfile.TemporaryDirectory(prefix="nwis-upload-ocr-") as directory:
        pdf_path = Path(directory) / "source.pdf"
        pdf_path.write_bytes(content)
        return OCRParser().extract_scanned_text(str(pdf_path), page_numbers)


@router.get("/{document_name}/source")
async def get_document_source(document_name: str):
    path = next((path for path in reports().values() if path.name == document_name), None)
    if path:
        text = path.read_text(encoding="utf-8")
        pages = []
        current = []
        page_number = 1
        for line in text.splitlines():
            marker = re.match(r"\s*\[PAGE\s+(\d+)\]\s*", line, re.I)
            if marker:
                if current:
                    pages.append({"page_number": page_number, "text": "\n".join(current)})
                page_number = int(marker.group(1))
                current = [line]
            else:
                current.append(line)
        if current:
            pages.append({"page_number": page_number, "text": "\n".join(current)})
        return {"document_name": path.name, "source_format": "text", "physical_pdf_available": False,
                "provenance": "synthetic", "text": text, "pages": pages}
    row = store.document(document_name)
    if not row:
        raise HTTPException(404, "Source report not found")
    import json
    return {"document_name": row["document_id"], "original_name": row["original_name"],
            "source_format": row["source_format"], "physical_pdf_available": bool(row["physical_pdf_available"]),
            "provenance": row["provenance"], "text": row["text"], "pages": json.loads(row["pages"]),
            "status": row["status"]}


@router.get("/{document_name}/file")
async def get_document_file(document_name: str):
    row = store.document(document_name)
    if not row or not row["physical_pdf_available"]:
        raise HTTPException(404, "Physical PDF not available")
    path = store.data_dir() / row["stored_name"]
    if not path.is_file():
        raise HTTPException(404, "Stored PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=row["original_name"])


@router.get("/evidence")
async def get_evidence_chunks(well_id: str = "NHK-421", depth: float = 2845.0):
    from ..services.orchestrator import DomainOrchestrator
    orc = DomainOrchestrator()
    orc.refresh_knowledge()
    intervals = source_formations(well_id)
    if intervals is None:
        raise HTTPException(404, "Well formations not found")
    interval = next((row for row in intervals
                     if row.get("md_top") is not None and row.get("md_bottom") is not None
                     and row["md_top"] <= depth < row["md_bottom"]), None)
    if interval is None:
        return []
    results = orc.retriever.retrieve(query="stuck pipe packoff coal caving",
                                     formation=interval["formation_name"], depth_md=depth, limit=4)
    return [{**chunk, "source_path": f"/api/v1/documents/{chunk['document_name']}/source"}
            for chunk in results if chunk.get("document_name")]
