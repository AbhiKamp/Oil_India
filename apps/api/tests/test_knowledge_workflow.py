import asyncio
import io
import os
import shutil
import subprocess
import sys
import tempfile

import httpx
import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("NWIS_DATA_DIR", str(tmp_path / "nwis"))
    transport = httpx.ASGITransport(app=app)

    async def request(method, url, **kwargs):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as session:
            return await session.request(method, url, **kwargs)

    return request


def run(coro):
    return asyncio.run(coro)


def pdf_bytes(pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=300, height=300)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def pdf_with_event_on_second_page():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    page = writer.add_blank_page(width=300, height=300)
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    }))
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    stream_object = DecodedStreamObject()
    stream_object.set_data(b"BT /F1 10 Tf 20 250 Td (Incident Type: GAS KICK) Tj 0 -15 Td (Depth: 321 m MD) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream_object)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def image_only_pdf_with_event():
    magick = shutil.which("magick")
    font = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
    if not magick or not os.path.isfile(font):
        pytest.skip("ImageMagick and Liberation Sans are required for the scanned-PDF fixture")
    with tempfile.TemporaryDirectory(prefix="nwis-test-image-") as directory:
        image_path = os.path.join(directory, "scan.jpg")
        subprocess.run([
            magick, "-size", "1800x600", "xc:white", "-font", font, "-pointsize", "48",
            "-fill", "black", "-gravity", "center", "-annotate", "+0-55", "Incident Type: GAS KICK",
            "-annotate", "+0+35", "Depth: 321 m MD | Formation: Barail", "-quality", "95", image_path,
        ], check=True, capture_output=True, timeout=15)
        pdf_path = os.path.join(directory, "scan.pdf")
        subprocess.run([magick, image_path, "-resize", "612x204!", "-density", "72", pdf_path],
                       check=True, capture_output=True, timeout=15)
        with open(pdf_path, "rb") as pdf_file:
            return pdf_file.read()


def upload(file_bytes, filename="report.txt", well_id="DEMO-1", provenance="synthetic"):
    return {"file": (filename, file_bytes), "well_id": (None, well_id), "provenance": (None, provenance)}


def test_upload_deduplicates_and_keeps_provenance_and_safe_storage(client, tmp_path):
    source = ("Incident Type: PACK-OFF\nDepth: 123.5 m MD | Stratigraphy: Sand\nDetails here\n").encode()
    async def check():
        first = await client("POST", "/api/v1/documents", files=upload(source, "../../unsafe.txt", provenance="user_supplied"))
        second = await client("POST", "/api/v1/documents", files=upload(source, "again.txt", provenance="user_supplied"))
        conflict = await client("POST", "/api/v1/documents", files=upload(source, "other.txt", provenance="synthetic"))
        assert first.status_code == second.status_code == 200
        assert conflict.status_code == 409
        a, b = first.json(), second.json()
        assert a["document_id"] == b["document_id"]
        assert b["deduplicated"] is True
        assert a["provenance"] == "user_supplied"
        assert a["events"][0]["measured_depth_md_m"] == 123.5
        assert a["events"][0]["review_state"] == "needs_review"
        listed_event = (await client("GET", "/api/v1/events", params={"well_id": "DEMO-1"})).json()[0]
        assert listed_event["provenance"] == "user_supplied"
        assert listed_event["original_name"] == "unsafe.txt"
        listing = (await client("GET", "/api/v1/documents")).json()
        listed = next(item for item in listing if item.get("document_id") == a["document_id"])
        assert listed["original_name"] == "unsafe.txt"
        assert "/" not in listed["document_name"]
        return a
    result = run(check())
    assert len(list((tmp_path / "nwis").glob("*.txt"))) == 1


def test_event_extracts_adjacent_preceding_metadata_without_cross_event_leak(client):
    content = (b"Depth: 100 m MD | Formation: Barail\nIncident Type: FIRST EVENT\n"
               b"Description: prior event details\nIncident Type: SECOND EVENT\nNo second event metadata\n")
    async def check():
        response = await client("POST", "/api/v1/documents", files=upload(content))
        first, second = response.json()["events"]
        assert first["measured_depth_md_m"] == 100
        assert first["formation"] == "Barail"
        assert second["measured_depth_md_m"] is None
        assert second["formation"] is None
    run(check())


def test_pdf_pages_are_physical_and_malformed_pdf_rejected(client):
    async def check():
        oversized_text = await client("POST", "/api/v1/documents", files=upload(b"a" * 2_000_001))
        assert oversized_text.status_code == 413
        malformed = await client("POST", "/api/v1/documents", files=upload(b"%PDF-not a PDF", "broken.pdf"))
        assert malformed.status_code == 422
        too_many_pages = await client("POST", "/api/v1/documents", files=upload(pdf_bytes(101), "large.pdf"))
        assert too_many_pages.status_code == 413
        response = await client("POST", "/api/v1/documents", files=upload(pdf_bytes(2), "scan.pdf"))
        assert response.status_code == 200
        doc = response.json()
        assert doc["physical_pdf_available"] is True
        assert doc["status"] == "needs_ocr"
        source = await client("GET", f"/api/v1/documents/{doc['document_id']}/source")
        assert [page["page_number"] for page in source.json()["pages"]] == [1, 2]
        physical = await client("GET", f"/api/v1/documents/{doc['document_id']}/file")
        assert physical.status_code == 200 and physical.content.startswith(b"%PDF-")
        assert physical.headers["content-disposition"].startswith("inline;")
        assert physical.headers["x-content-type-options"] == "nosniff"
        return doc
    run(check())


def test_extracted_pdf_event_uses_actual_physical_page_number(client):
    async def check():
        response = await client("POST", "/api/v1/documents", files=upload(pdf_with_event_on_second_page(), "events.pdf"))
        assert response.status_code == 200
        event = response.json()["events"][0]
        assert event["measured_depth_md_m"] == 321
        assert event["page_marker"] == 2
        assert event["page_reference_type"] == "physical_pdf_page"
        assert event["extraction_method"] == "pdf_text"
    run(check())


def test_real_ocr_extracts_event_from_image_only_pdf(client):
    from pypdf import PdfReader

    scanned = image_only_pdf_with_event()
    assert PdfReader(io.BytesIO(scanned)).pages[0].extract_text() in (None, "")
    async def check():
        response = await client("POST", "/api/v1/documents", files=upload(scanned, "scanned.pdf"))
        assert response.status_code == 200
        doc = response.json()
        assert doc["status"] == "extracted"
        assert doc["extraction_status"] == "complete (OCR applied to scanned pages)"
        source = await client("GET", f"/api/v1/documents/{doc['document_id']}/source")
        page = source.json()["pages"][0]
        assert page["extraction_method"] == "ocr"
        event = doc["events"][0]
        assert event["event_type"].upper().startswith("GAS KICK")
        assert event["measured_depth_md_m"] == 321
        assert "barail" in event["formation"].casefold()
        assert event["page_reference_type"] == "physical_pdf_page"
        assert event["extraction_method"] == "ocr"
        assert "confidence" not in event
    run(check())


def test_ocr_reports_missing_system_tools():
    from services.document_intelligence.parsers.ocr_parser import OCRParser, OCRUnavailableError

    with pytest.raises(OCRUnavailableError, match="OCR unavailable: missing"):
        OCRParser(tesseract_cmd="missing-tesseract-nwis", pdftoppm_cmd="missing-pdftoppm-nwis")\
            .extract_scanned_text("unused.pdf", [1])


def test_source_review_and_decisions_survive_reopen(client):
    content = b"Incident Type: PACK-OFF\nDepth: 200 m MD | Formation: Barail\nEvidence excerpt.\n"
    async def check():
        uploaded = (await client("POST", "/api/v1/documents", files=upload(content))).json()
        event = uploaded["events"][0]
        operational = await client("GET", "/api/v1/events", params={"well_id": "DEMO-1", "review_state": "approved"})
        assert operational.json() == []
        source = await client("GET", f"/api/v1/documents/{uploaded['document_id']}/source")
        assert "Evidence excerpt" in source.json()["text"]
        assert source.json()["pages"][0]["page_number"] == 1
        changed = await client("PATCH", f"/api/v1/events/{event['event_id']}/review", json={
            "review_state": "approved", "reviewer": "Engineer", "event_type": "Reviewed pack-off"})
        assert changed.status_code == 200
        assert changed.json()["event_type"] == "Reviewed pack-off"
        assert changed.json()["audit"][0]["original_values"]["event_type"] == "PACK-OFF"
        note = {"well_id": "DEMO-1", "event_id": event["event_id"], "note": "Reviewed for handover",
                "actor": "Engineer", "status": "monitoring"}
        decision = await client("POST", "/api/v1/decisions", json=note)
        assert decision.status_code == 200
        assert decision.json()["source_snapshot"]["event_type"] == "Reviewed pack-off"
        # Each request opens a fresh HTTP client/database connection; values persist in SQLite.
        fetched = (await client("GET", "/api/v1/events", params={"well_id": "DEMO-1"})).json()
        assert fetched[0]["review_state"] == "approved"
        decisions = (await client("GET", "/api/v1/decisions", params={"well_id": "DEMO-1"})).json()
        assert decisions[0]["note"] == "Reviewed for handover"
    run(check())


def test_decision_accepts_known_active_target_and_rejects_unknown_target(client):
    async def check():
        missing_event = await client("POST", "/api/v1/decisions", json={"well_id": "NHK-412", "event_id": "missing",
            "note": "note", "actor": "Engineer", "status": "acknowledged"})
        assert missing_event.status_code == 404
        events = (await client("GET", "/api/v1/events", params={"well_id": "NHK-412"})).json()
        event_id = events[0]["event_id"]
        accepted = await client("POST", "/api/v1/decisions", json={"well_id": "NHK-421", "event_id": event_id,
            "note": "note", "actor": "Engineer", "status": "acknowledged"})
        assert accepted.status_code == 200
        snapshot = accepted.json()["source_snapshot"]
        assert snapshot["source_well_id"] == "NHK-412"
        assert snapshot["target_well_id"] == "NHK-421"
        unknown_target = await client("POST", "/api/v1/decisions", json={"well_id": "UNKNOWN", "event_id": event_id,
            "note": "note", "actor": "Engineer", "status": "acknowledged"})
        assert unknown_target.status_code == 404
        blank = await client("POST", "/api/v1/decisions", json={"well_id": "NHK-412", "event_id": event_id,
            "note": " ", "actor": "Engineer", "status": "acknowledged"})
        assert blank.status_code == 422
    run(check())


def test_unreviewed_or_rejected_upload_cannot_be_used_for_decision(client):
    async def check():
        uploaded = (await client("POST", "/api/v1/documents", files=upload(
            b"Incident Type: PACK-OFF\nDepth: 123 m MD\n", well_id="DEMO-1"))).json()
        event = uploaded["events"][0]
        decision = {"well_id": "NHK-421", "event_id": event["event_id"], "note": "note",
                    "actor": "Engineer", "status": "acknowledged"}
        unreviewed = await client("POST", "/api/v1/decisions", json=decision)
        assert unreviewed.status_code == 409
        await client("PATCH", f"/api/v1/events/{event['event_id']}/review", json={
            "review_state": "rejected", "reviewer": "Engineer"})
        rejected = await client("POST", "/api/v1/decisions", json=decision)
        assert rejected.status_code == 409
    run(check())


def test_evidence_uses_active_formation_and_source_api_urls(client):
    async def check():
        uploaded = (await client("POST", "/api/v1/documents", files=upload(
            b"Depth: 3000 m MD | Formation: Barail Coal-Shale\n"
            b"Incident Type: STUCK PIPE PACK-OFF\nObserved stuck pipe packoff in coal.\n",
            well_id="DEMO-EVIDENCE", provenance="user_supplied"))).json()
        event = uploaded["events"][0]
        approved = await client("PATCH", f"/api/v1/events/{event['event_id']}/review", json={
            "review_state": "approved", "reviewer": "Engineer"})
        assert approved.status_code == 200
        barail = (await client("GET", "/api/v1/documents/evidence", params={"well_id": "NHK-421", "depth": 3000})).json()
        assert any(item["document_name"] == uploaded["document_id"] for item in barail)
        assert all(item["source_path"].startswith("/api/v1/documents/") for item in barail)
        assert all(item["formation_name"] == "Barail Coal-Shale" for item in barail)
        girujan = await client("GET", "/api/v1/documents/evidence", params={"well_id": "NHK-421", "depth": 2000})
        assert all(item["formation_name"] == "Girujan Clay" for item in girujan.json())
        assert not any(item["document_name"] == uploaded["document_id"] for item in girujan.json())
    run(check())


def test_storage_failure_leaves_no_document_metadata(client, monkeypatch):
    from apps.api.app.services import knowledge_store

    def fail_write(*args, **kwargs):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(knowledge_store, "_write_content", fail_write)
    async def check():
        response = await client("POST", "/api/v1/documents", files=upload(b"ordinary text"))
        assert response.status_code == 507
        names = [item.get("document_id") for item in (await client("GET", "/api/v1/documents")).json()]
        assert not any(names)
    run(check())
