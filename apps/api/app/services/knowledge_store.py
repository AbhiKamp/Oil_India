"""Small persistent SQLite store for locally uploaded evidence and decisions."""

import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def data_dir() -> Path:
    path = Path(os.environ.get("NWIS_DATA_DIR", PROJECT_ROOT / ".local" / "nwis"))
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def known_wells() -> set[str]:
    path = PROJECT_ROOT / "data" / "synthetic" / "wells" / "wells.json"
    try:
        wells = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {well["well_id"].casefold() for well in wells if isinstance(well.get("well_id"), str)}


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(data_dir() / "knowledge.sqlite3", timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY, content_hash TEXT UNIQUE NOT NULL,
            original_name TEXT NOT NULL, stored_name TEXT NOT NULL, well_name TEXT NOT NULL,
            provenance TEXT NOT NULL, source_format TEXT NOT NULL, status TEXT NOT NULL,
            pages TEXT NOT NULL, text TEXT NOT NULL, physical_pdf_available INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(document_id),
            well_id TEXT NOT NULL, event_type TEXT NOT NULL, measured_depth_md_m REAL,
            formation TEXT, excerpt TEXT NOT NULL, page_marker INTEGER,
            page_reference_type TEXT NOT NULL, review_state TEXT NOT NULL,
            mitigation TEXT, outcome TEXT, audit TEXT NOT NULL DEFAULT '[]',
            extraction_method TEXT NOT NULL DEFAULT 'pdf_text'
        );
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT, well_id TEXT NOT NULL,
            event_id TEXT NOT NULL, note TEXT NOT NULL, actor TEXT NOT NULL,
            status TEXT NOT NULL, source_snapshot TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS builtin_reviews (
            event_id TEXT PRIMARY KEY, current_values TEXT NOT NULL, audit TEXT NOT NULL
        );
    """)
    columns = {row["name"] for row in db.execute("PRAGMA table_info(events)")}
    if "extraction_method" not in columns:
        db.execute("ALTER TABLE events ADD COLUMN extraction_method TEXT NOT NULL DEFAULT 'pdf_text'")
    return db


@contextmanager
def connection():
    db = connect()
    try:
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def _write_content(stored_name: str, content: bytes) -> None:
    directory = data_dir()
    descriptor, temporary = tempfile.mkstemp(prefix=".upload-", dir=directory)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, directory / stored_name)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uploaded_documents() -> list[dict[str, Any]]:
    with connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM documents ORDER BY created_at")]


def document(document_name: str) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT * FROM documents WHERE document_id=?", (document_name,)).fetchone()
    return dict(row) if row else None


def events_for(well_id: str | None = None) -> list[dict[str, Any]]:
    with connection() as db:
        rows = db.execute("SELECT events.*, documents.document_id AS source_file, "
                          "documents.provenance, documents.original_name FROM events "
                          "JOIN documents USING(document_id)" +
                          (" WHERE well_id=?" if well_id else "") + " ORDER BY events.rowid",
                          (well_id,) if well_id else ()).fetchall()
    output = []
    for row in rows:
        event = dict(row)
        event.pop("audit", None)
        output.append(event)
    return output


def list_events(well_id: str | None = None, q: str | None = None,
                review_state: str | None = None) -> list[dict[str, Any]]:
    """List bundled and uploaded events; pass approved to exclude unreviewed records."""
    from .report_data import events as source_events

    result = []
    for item in source_events(well_id):
        item.update({"review_state": "approved",
                     "provenance": "synthetic", "original_name": item["source_file"],
                     "extraction_method": "text"})
        item.update(builtin_review(item["event_id"]) or {})
        result.append(item)
    result.extend(events_for(well_id))
    if q:
        query = q.casefold()
        result = [item for item in result if query in " ".join(str(item.get(key) or "") for key in
                  ("event_type", "formation", "excerpt", "well_id", "original_name")).casefold()]
    if review_state:
        result = [item for item in result if item.get("review_state") == review_state]
    return result


def event(event_id: str) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT events.*, documents.document_id AS source_file, "
                         "documents.provenance, documents.original_name FROM events "
                         "JOIN documents USING(document_id) WHERE event_id=?", (event_id,)).fetchone()
    return dict(row) if row else None


def insert_upload(*, content: bytes, original_name: str, well_id: str, provenance: str,
                  extension: str, pages: list[dict[str, Any]], events: list[dict[str, Any]],
                  status: str) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    digest = hashlib.sha256(content).hexdigest()
    doc_id = f"upload-{digest[:24]}"
    stored_name = f"{digest}.{extension}"
    text = "\n\n".join(page["text"] for page in pages)
    wrote_file = False
    try:
        with connection() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT * FROM documents WHERE content_hash=?", (digest,)).fetchone()
            if prior:
                if (prior["well_name"] != well_id or prior["provenance"] != provenance or
                        prior["source_format"] != extension):
                    raise ValueError("Identical content already exists with different well or provenance")
                prior_events = db.execute("SELECT events.*, documents.document_id AS source_file FROM events "
                                          "JOIN documents USING(document_id) WHERE events.document_id=? ORDER BY events.rowid",
                                          (prior["document_id"],)).fetchall()
                return dict(prior), [dict(row) for row in prior_events], False
            _write_content(stored_name, content)
            wrote_file = True
            created = now()
            db.execute("""INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                       (doc_id, digest, original_name[:255], stored_name, well_id, provenance,
                        extension, status, json.dumps(pages), text, int(extension == "pdf"), created))
            output = []
            for index, item in enumerate(events):
                event_id = f"{doc_id}:{index}"
                record = {**item, "event_id": event_id, "well_id": well_id, "source_file": doc_id}
                db.execute("""INSERT INTO events(event_id,document_id,well_id,event_type,measured_depth_md_m,
                    formation,excerpt,page_marker,page_reference_type,review_state,mitigation,outcome,extraction_method)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (event_id, doc_id, well_id, record["event_type"], record["measured_depth_md_m"],
                     record["formation"], record["excerpt"], record["page_marker"],
                     record["page_reference_type"], record["review_state"], record.get("mitigation"),
                     record.get("outcome"), record.get("extraction_method", "text")))
                output.append(record)
    except BaseException:
        if wrote_file:
            (data_dir() / stored_name).unlink(missing_ok=True)
        raise
    return {"document_id": doc_id, "content_hash": digest, "original_name": original_name[:255],
            "stored_name": stored_name, "well_name": well_id, "provenance": provenance,
            "source_format": extension, "status": status, "pages": json.dumps(pages), "text": text,
            "physical_pdf_available": int(extension == "pdf"), "created_at": created}, output, True


def builtin_review(event_id: str) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT current_values FROM builtin_reviews WHERE event_id=?", (event_id,)).fetchone()
    return json.loads(row["current_values"]) if row else None


def save_review(event_id: str, changes: dict[str, Any], reviewer: str,
                base: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT * FROM events WHERE event_id=?", (event_id,)).fetchone()
        if not row:
            old = db.execute("SELECT * FROM builtin_reviews WHERE event_id=?", (event_id,)).fetchone()
            if old:
                current = json.loads(old["current_values"])
                audit = json.loads(old["audit"])
            elif base:
                current = base
                audit = []
            else:
                return None
            audit.append({"reviewer": reviewer, "at": now(),
                          "original_values": {key: current.get(key) for key in changes}})
            current.update(changes)
            db.execute("INSERT OR REPLACE INTO builtin_reviews VALUES(?,?,?)",
                       (event_id, json.dumps(current), json.dumps(audit)))
            return {**current, "audit": audit}
        current = dict(row)
        audit = json.loads(current["audit"])
        changed = {key: current[key] for key in changes}
        audit.append({"reviewer": reviewer, "at": now(), "original_values": changed})
        assignments = ",".join(f"{key}=?" for key in changes)
        db.execute(f"UPDATE events SET {assignments}, audit=? WHERE event_id=?",
                   (*changes.values(), json.dumps(audit), event_id))
        updated = dict(db.execute("SELECT events.*, documents.document_id AS source_file FROM events "
                                  "JOIN documents USING(document_id) WHERE event_id=?", (event_id,)).fetchone())
        updated["audit"] = json.loads(updated["audit"])
        return updated


def save_decision(well_id: str, source_event: dict[str, Any], note: str, actor: str,
                  status: str) -> dict[str, Any]:
    snapshot = {key: source_event.get(key) for key in (
        "event_id", "well_id", "event_type", "measured_depth_md_m", "formation", "excerpt",
        "source_file", "page_marker", "page_reference_type", "review_state", "mitigation", "outcome",
        "provenance", "original_name", "extraction_method")}
    snapshot["source_well_id"] = source_event["well_id"]
    snapshot["target_well_id"] = well_id
    with connection() as db:
        cursor = db.execute("""INSERT INTO decisions(well_id,event_id,note,actor,status,source_snapshot,created_at)
            VALUES(?,?,?,?,?,?,?)""", (well_id, source_event["event_id"], note, actor, status,
                                         json.dumps(snapshot), now()))
        row = dict(db.execute("SELECT * FROM decisions WHERE decision_id=?", (cursor.lastrowid,)).fetchone())
    row["source_snapshot"] = json.loads(row["source_snapshot"])
    return row


def decisions_for(well_id: str | None = None) -> list[dict[str, Any]]:
    with connection() as db:
        rows = db.execute("SELECT * FROM decisions" + (" WHERE well_id=?" if well_id else "") +
                          " ORDER BY decision_id", (well_id,) if well_id else ()).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["source_snapshot"] = json.loads(item["source_snapshot"])
        result.append(item)
    return result
