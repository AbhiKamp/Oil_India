# StrataSentry NWIS

### Before the next metre, learn from the last well.

**Nearby Wells Intelligence System** · SIH 2026 · Problem Statement **26121** · Oil India Limited

**Healix 1 — Team 172547** · [Repository](https://github.com/Fadhil006/Oil_India) · [Submitted presentation](Healix-1_SIH-2026_PS-26121_Submission.pdf)

eRTMAC provides the current drilling picture. NWIS connects it to historical well experience: **what happened, in which formation, where the evidence is, and what the previous crew recorded.** It is a read-only decision-support prototype, not a rig-control system or an eRTMAC replacement.

## The demonstration

1. Select the active synthetic well and change the nearby-well radius.
2. Compare the supplied formation intervals across wells, not just their raw depths.
3. Review the historical interval ahead. Open the original source excerpt and its provenance.
4. Upload a text or scanned PDF, inspect extraction, and approve or correct event fields.
5. Replay a normal, pack-off, or kick scenario; distinguish current signal indications from historical precedent.
6. Record an engineer's acknowledgement and note for shift handover. Its source snapshot survives a restart.

All bundled well data and incidents are **synthetic**, not OIL operational records. The active-well tops are an explicit synthetic prognosis. Formation-top-relative mapping is an approximate comparison, **not validated subsurface correlation**. A distance to a comparable interval is not a countdown to failure.

## Run locally

The API reads the bundled scenario directly; external databases and the legacy seed script are **not required** for this local profile.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r apps/api/requirements.txt
uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd apps/dashboard
npm ci
npm run dev
```

Open **http://localhost:3000**. API contracts: **http://127.0.0.1:8000/docs**. Set `NEXT_PUBLIC_API_URL` when using a different API address. If port 3000 is occupied, use `npm run dev -- --port 3010` or another free port.

The Operations screen has explicit synthetic replay controls. A CLI replay is also available from the root:

```bash
source .venv/bin/activate
python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff --reset
```

`--reset` clears in-memory synthetic telemetry, **not** saved sources or decisions. Replay controls are disabled outside `ENVIRONMENT=development`. This is a local demonstration profile with self-entered reviewer names, not an authenticated production deployment.

### Document extraction

- UTF-8 TXT and text PDFs work with the Python requirements above.
- Optional scanned-page OCR uses locally installed **Tesseract** and **Poppler (`pdftoppm`)**. No cloud OCR is used. If tools are absent or recognition fails, the document explicitly remains `needs_ocr`.
- Upload limit: 10 MiB; PDF limit: 100 pages; automatic OCR limit: 10 scanned pages; extracted text limit: 2 million characters.
- Uploaded files and SQLite records live under ignored `.local/nwis/`. Set `NWIS_DATA_DIR` for another location. Back up that directory to retain local knowledge and handover notes.
- Uploaded records need review before operational retrieval. Physical PDF page references are distinct from the markers in bundled synthetic text reports.

## What is implemented—and what is not

| Capability | Current local prototype |
| --- | --- |
| Nearby wells | Coordinate-based interactive schematic, Haversine radius filtering and distances; not a tiled basemap |
| Formation context | Source-parsed offset intervals and labeled synthetic active-well prognosis; approximate formation-relative historical watch |
| Institutional memory | Persistent documents, extracted events, source/page provenance, review corrections, and saved decision snapshots |
| OCR | Actual optional local Tesseract/Poppler pipeline, bounded and tested on an image-only fixture |
| Retrieval | Deterministic local lexical matching of approved evidence; no random “semantic” vectors or remote Qdrant requirement |
| Assistant | Extractive evidence summary with exact source excerpts and abstention; **not a language model** |
| Telemetry | Deterministic synthetic replay, well-isolated windows, timestamp-aware derivatives and input validation |
| Risk indication | Explicitly uncalibrated heuristic rules; no incident-time prediction or autonomous actions |
| Experimental ML | Reproducibly trained NumPy classifier with grouped synthetic holdout evaluation; isolated from alert generation |
| eRTMAC connectivity | Proposed read-only adapter boundary; no real OIL connection has been established |
| Deployment | Laptop-local profile; enterprise infrastructure files describe intended architecture, not proven readiness |

The small experimental model classifies **current generated patterns**, not future incidents. Its [evaluation](models/experimental/artifacts/evaluation.json) includes denominators, confusion matrix, a majority baseline, and synthetic-data limitations. Do not interpret generated-data accuracy as field reliability, prevented incidents, or NPT reduction.

## Verification

From the root, with the Python environment activated:

```bash
python -m pytest services/ tests/ apps/api/tests/ -q
```

The root `pytest.ini` uses importlib mode for the existing hyphenated service directories. API service-package aliases work on Linux without Windows junctions.

Dashboard production build, inside `apps/dashboard`:

```bash
npm run build
npm audit --audit-level=high
```

Synthetic classifier reproduction:

```bash
python -m models.experimental.train
python -m pytest tests/test_experimental_model.py -q
```

See [delivery status](docs/delivery-status.md) for the latest measured checks and remaining limitations. A passing suite exercises the synthetic prototype; it does not certify drilling safety.

## The film: Before the Next Metre

The isolated video workspace is [`apps/video/`](apps/video/README.md). Its Remotion source, capture runner, narration/transcript assets, and [storyboard](docs/video-plan.md) are separate from the dashboard. Real product interactions must be captured from the running application; explanatory geology remains labeled illustrative.

```bash
cd apps/video
npm ci
# Generate the recorded capture/audio inputs first (see apps/video/README.md).
npm run studio
# When rendering with a system browser:
npm run render -- --browser-executable=/usr/bin/chromium
```

Rendered media lives in ignored `out/` directories and is not committed as a large Git blob. The official open-source Remotion agent skill is installed under `.agents/skills/`; source and hash are in `skills-lock.json`.

## Repository guide

| Path | Role |
| --- | --- |
| `apps/api/` | FastAPI gateway, local persistence, ingestion/review, replay, and typed endpoints |
| `apps/dashboard/` | Next.js 15 / React 18 operations, source workbench, and handover interface |
| `apps/video/`, `demo/capture/` | Remotion film and reproducible application capture |
| `services/` | Geometry, parsing/OCR, telemetry, correlation, heuristics, physics, retrieval, and fusion modules |
| `models/experimental/` | Actual trained synthetic-pattern classifier and reproducible evaluation |
| `data/synthetic/`, `demo/` | Explicitly synthetic demonstration inputs |
| `tests/`, `apps/api/tests/` | Domain, integration, API, replay, and workflow checks |
| `docs/` | Product plan, film plan, implementation handoff, and measured delivery status |
| `database/`, `infrastructure/`, `architecture/` | Optional/intended deployment designs; not required for the verified local profile |

## Scope and safety

NWIS surfaces historical records for qualified engineering review. Historical actions are not automatically suitable for another well. The prototype does not set operating limits, control equipment, infer safe kill procedures, or guarantee risk detection. Production access control, large-corpus performance, field model evaluation, real eRTMAC integration, and deployment validation remain separate engineering work.

Licensed under [Apache 2.0](LICENSE). Third-party skills and media retain their own terms; see source credits alongside the video assets.
