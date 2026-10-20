# StrataSentry NWIS — prototype delivery plan

Status: proposed implementation; no application changes made in this planning pass.

Prepared for **Healix 1 · Team 172547 · SIH 2026 · PS 26121**.
Repository: <https://github.com/Fadhil006/Oil_India>
Submission: [submitted presentation](../Healix-1_SIH-2026_PS-26121_Submission.pdf).

## Reading order

1. This document: product, current gaps, architecture, data, and acceptance criteria.
2. [Film treatment and storyboard](video-plan.md): the primary presentation deliverable.
3. [Execution handoff](implementation-handoff.md): work packages, ownership, dependencies, and release gates.

## 1. The proposition

**Before the next metre, learn from the last well.**

Oil India already sees what is happening through eRTMAC. NWIS adds what happened before, where it happened, what was tried, and what outcome was recorded. It brings that evidence to the engineer before the active well reaches a comparable interval.

The prototype must tell one complete story:

> A drilling engineer approaches a formation where an offset well previously encountered trouble. NWIS retrieves the original report, aligns the historical interval with the active well, flags the approaching risk, and presents the recorded mitigation for engineering review. The engineer records a decision, preserving the lesson for the next shift.

The memorable differentiator is the **traceable connection between an old report and a current drilling decision**. A chatbot, a rotating well, and a numerical risk score are supporting features, not the proposition.

### Success conditions

- After one viewing, a non-specialist can explain the problem, the input data, the transformation, the warning, and the engineer's role.
- A judge can click from an alert to an actual page containing the underlying historical evidence.
- Radius changes, well selection, evidence filters, and replay controls change real application state.
- A formation-aligned comparison visibly explains why the closest surface well is not always the best analogue.
- The live demo works on a prepared laptop without external internet.
- Every quantitative claim has a measurement, explicit synthetic label, or published source.
- All seven expected outcomes in the problem statement have a working demonstration or a clearly stated scope boundary.

Winning cannot be guaranteed. These conditions optimize for clarity, credibility, differentiation, and demonstrability rather than feature count.

## 2. Repository assessment

Assessment is based on source inspection on 20 October 2026, not a completed runtime audit. Application builds and tests were not run during this planning pass. Existing tests are starting material, not proof that the checkout works.

| Area | Observed source evidence | Required work |
| --- | --- | --- |
| Identity | README and architecture expand NWIS as “National Well Intelligence System” | Correct to **Nearby Wells Intelligence System** throughout public surfaces |
| Dashboard startup | `apps/dashboard/app/page.tsx` imports `../lib/types` and `../lib/api`; `apps/dashboard/lib/` is absent | Restore typed contracts/client before visual development |
| Python packaging | API imports underscore service names; source directories use hyphens; `scripts/link_services.py` hardcodes a Windows path and junction command | Make imports work from a clean Linux checkout; choose one package convention and update callers |
| Map | Main page renders a well profile, telemetry, alert, and evidence panels; wells route offers list/detail only | Add real coordinate-based radius search and interactive geographic map |
| Well profiles | `WellViewer3D.tsx` uses a 2D canvas and constructs MOR-118's path procedurally | Render supplied surveys for each well; do not imply fabricated geometry is measured |
| Trajectories | `routes/trajectory.py` returns NHK-421's trajectory for every requested ID | Per-well data and unknown-well errors |
| Formation context | Same fixed tops returned for every well; orchestrator infers formation from one MD threshold | Store per-well tops, reference datum, uncertainty, and correlation method |
| Documents | `routes/documents.py` returns three fixed document listings; no upload route | Persistent ingestion, review, evidence records, source-page viewing |
| Citations | Orchestrator assigns formation, depth, and page numbers while loading text files | Extract actual source references and preserve them end to end |
| Retrieval | Qdrant call is `pass`; local cosine retrieval adds a raw-MD proximity bonus | Implement an honest retrieval mode and formation-aware filtering |
| Models | `stuck_pipe_model.py` sets `is_loaded=True` without loading a trained artifact and returns hand-written rules | Label baseline correctly; implement and evaluate an actual model separately |
| Copilot | `mistral_client.py` has a placeholder provider branch and fixed operational advice, including fallback citations without evidence | Ground answers in retrieved records; implement local model mode; abstain on missing support |
| State | Orchestrator uses one telemetry processor and loads one active trajectory | Isolate replay/telemetry by well and session; reset deterministically |
| Connectivity | Dashboard always displays “AIR-GAP STANDALONE” | Display observed source freshness, local readiness, and model availability |
| Claims | README asserts enterprise readiness and 15–45 minute warning | Replace with verified prototype capabilities and measured replay results |

### What to reuse

Keep Next.js, React, TypeScript, the FastAPI gateway, current component boundaries, survey calculations, synthetic corpus layout, and useful domain tests. Three.js is already declared; use it for a real scene if it improves spatial explanation. Review the existing parsers, extractors, correlation code, and physics functions before replacing them.

Do not rewrite the repository from scratch. Do not make Kafka, distributed workers, multiple databases, or a new UI framework prerequisites for a reliable local demonstration.

## 3. Scope and problem-statement coverage

| Required outcome | Prototype implementation | Proof in demo |
| --- | --- | --- |
| AI/NLP/OCR extraction | Upload text PDF and scanned PDF; extract typed events with source references; review uncertain fields | Original paragraph becomes an editable, cited event card |
| Nearby wells | Geographic map, active well, radius input, matching list, distance labels | Changing radius changes the candidate set |
| Knowledge repository | Search events, lessons, mitigations, outcomes; filter by formation, well, event type | Search result opens the correct source page |
| Cross-well correlation | Side-by-side formation tracks, surveys, MD/TVD labels, equivalent risk interval | Same formation aligns despite different raw depths |
| Predictive analytics | Interpretable baseline plus actual evaluated experimental ML; pack-off/stuck-pipe and kick focus | Replay raises a sourced warning with method and contributing signals |
| Alerts/recommendations | Historical approach watch, telemetry escalation, evidence, recorded mitigation, acknowledgement | One alert persists through acknowledgement and decision notes |
| Usable dashboard | Coherent map → correlation → evidence → decision workspace | All views stay synchronized to the same well and interval |

### Priority boundaries

**P0 — release gates:** startup; coherent synthetic dataset; source ingestion; radius map; formation alignment; evidence-backed historical watch; pack-off replay; grounded Q&A; decision log; polished film; clean-checkout instructions.

**P1 — required before calling the prototype broadly demonstrated:** scanned-document OCR; second kick scenario; actual experimental ML evaluation; local model answers; verified internet-disconnected run; casing/mud/cementing comparison with source links.

**P2 — only after film and core proof are strong:** constrained GR/resistivity DTW, expanded reservoir tracks, richer multi-well 3D rendering, additional model experiments.

Mud losses, torque spikes, overpressure indicators, fishing, NPT, and cementing events must be searchable structured records. Do not imply all have validated predictive models. Store casing and cementing practices with interval and outcome; missing data remains visibly missing.

No rig control, automatic drilling actions, invented operational setpoints, production eRTMAC integration claims, or trained-on-OIL claims. Actual integration depends on access and agreed schemas.

## 4. A single coherent demonstration dataset

Create a versioned scenario manifest under `demo/scenarios/`. Every screenshot, replay frame, report, narration number, and comparison derives from this manifest and the underlying data.

### Corpus

- One active synthetic well, four local offset wells, and one deliberately distant regional analogue.
- Eight to twelve short synthetic WCR/DDR documents, including two scanned examples and one ambiguous extraction requiring review.
- Twenty to thirty labeled event records with causes, recorded mitigations, outcomes, and page references.
- Distinct directional surveys and formation tops for all compared wells.
- Pack-off and kick replays plus a normal-operation control and a sensor-quality failure case.
- At least one near well in a different formation; at least one relevant same-formation well at a different depth.
- At least one report whose mitigation failed or whose outcome is unknown. Institutional memory should preserve unsuccessful actions too.

Use fictional well identifiers with a visible `DEMO` prefix for newly authored records. Existing IDs can be retained only with explicit synthetic provenance. Do not attach invented incidents to real OIL operations as fact.

The current NHK/MOR/BGH coordinates span different fields. Compute actual distances before reusing them; a regional analogue cannot silently appear inside a small nearby-well radius. Keep “Nearby wells” and “Regional analogues” separate, with a deliberate opt-in for the latter.

### Hero pack-off scenario

1. Active well approaches a mapped Barail interval; telemetry is initially normal.
2. Two approved historical events overlap the comparable interval. One is a strong analogue; another has weaker supporting data.
3. NWIS raises an **approaching historical risk interval** watch before sensor anomalies occur.
4. Replay later develops rising pressure, torque variability, and falling penetration rate. A distinct telemetry warning explains the escalation.
5. Engineer opens the cited page, reviews what the historical crew tried, and acknowledges the alert with a note.
6. Decision is saved for shift handover. Do not claim that acknowledgement itself prevented an incident or caused recovery.

Illustrative planning values: current position 24 m above the aligned interval; 12 m/hour recent ROP implies approximately two hours to interval entry. These are placeholders until the dataset is authored. Use consistent MD-to-TVD conversion: MD distance requires MD ROP; TVD distance requires projected vertical rate. Never present “time to formation” as “time until failure.” Suppress an estimate during a connection, zero ROP, reverse motion, or unreliable correlation.

### Data invariants

- All depths include units, reference type, and datum. MD is not interchangeable with TVD or TVDSS.
- Preserve original units and normalized values; validate top ≤ bottom.
- Survey stations are ordered; trajectories and bit locations use interpolation rather than snapping to a future station.
- Formation identity is canonicalized without erasing original report wording.
- Unknown depth, outcome, or cause stays null/unknown. Inferred fields are distinguishable from quoted facts.
- Report hashes and event IDs remain stable across re-ingestion; duplicate upload does not duplicate events.
- Source page numbers must refer to actual delivered pages, not numbers invented for visual realism.
- Replay includes timestamps, sequence numbers, operation state, quality flags, and scenario identity.

## 5. Product experience and visual direction

### Design concept: a subsurface mission-control desk

Interstellar-inspired scale, quiet, precision, and human stakes. Geological layers replace decorative galaxies; survey lines replace orbital paths. The interface remains recognizably an engineering tool.

Proposed tokens: near-black `#080C12`, panel `#111923`, ivory `#F1EEE6`, slate `#9BAAB9`, evidence cyan `#77C7D6`, caution amber `#E7B76C`, danger coral `#EC786B`. Validate contrast rather than assuming these combinations pass. Pair a locally bundled readable sans-serif with a tabular monospace for measurements. Avoid emoji controls and tiny neon labels.

### Screen A — Operations

- Persistent header: active well, formation, MD/TVD, replay/live source, timestamp/freshness.
- Left: geographic map and synchronized nearby-well list; radius control in kilometres.
- Center: selected spatial/correlation view, annotated bit position, comparable event intervals.
- Right: one highest-priority decision card answering **what, why now, evidence, next review**.
- Bottom: compact telemetry tracks with units and shared time cursor; replay controls clearly labeled.
- Default view answers “what deserves attention?” within five seconds.

### Screen B — Compare wells

- Three to four stratigraphic columns with formation, event bands, and optional logs.
- Toggle absolute TVD versus formation-relative view; animate the alignment once, then stop.
- Explain match factors individually: formation match, interval coverage, trajectory separation, data quality, event type.
- Show why a nearby candidate was excluded. Do not hide behind an unexplained “94% similar” badge.
- Supplemental tabs for mud, casing, cementing, and reservoir observations with citations.

### Screen C — Evidence workbench

- Source PDF on one side, structured event and extraction provenance on the other.
- Clickable page citation; highlight supported text when bounding boxes are available.
- Review workflow: uploaded → extracting → needs review → approved/rejected.
- Field corrections persist with original value, reviewer identity, and time.
- Index approved records for operational advice; uncertain records can appear in a clearly separated review queue.

### Screen D — Decision and handover

- Alert timeline: new → acknowledged → monitored/resolved, with explicit reasons.
- Historical mitigation is labeled “recorded action in offset well,” not a universal SOP.
- Engineer note and decision export contain the source links, live snapshot, and method version.
- Resolution requires recorded evidence or engineer action, not a timer or cinematic button.

### Screen E — Ask the knowledge base

- Contextual panel rather than a disconnected full-screen chatbot.
- Suggested questions: “Why this offset well?”, “What happened in this interval?”, “Which mitigation was recorded?”, “What evidence is missing?”
- Answer structure: finding, sources, limitations, relevant historical actions.
- Unsupported question returns an explicit evidence gap with useful filters to investigate.

### Interaction quality

Keyboard-operable controls, visible focus, text/icon severity labels, reduced-motion behavior, accessible non-canvas alternatives, chart units, loading/error/empty states, and usable 1366×768 layout. Avoid continuous camera rotation and pulsing alarms. Alerts must not obscure the source evidence.

## 6. Implementation architecture

### Default local profile

```text
Reports → parser/OCR → typed events → review → persistent knowledge store
Surveys + tops → geometry + formation alignment → candidate evidence
Replay/read-only source → per-well windows → rules/model → alert lifecycle
Knowledge + alignment + alert → API → operations/evidence/decision UI
Approved evidence → local retrieval → local LLM → verified cited answer
Actual application recordings → Remotion composition → submission film
```

Use the existing FastAPI process with domain modules and a persistent local SQLite database for the prototype. Reuse standard SQLite text search for the baseline; add local embeddings only when their model is available and the retrieval quality is measured. Qdrant/PostGIS/TimescaleDB can remain an optional deployment profile; do not keep a second supposedly equivalent implementation unless it is exercised.

Use an explicit background ingestion job with persisted status and bounded concurrency. A small local worker is sufficient; uploading a scanned PDF must not block telemetry. Include upload type/size limits, generated safe storage names, parse timeouts, and error reporting.

Keep local model inference optional for basic navigation and source search. If no model is installed, return a clearly labeled retrieved-evidence summary; never claim a template is a local Mistral response. For the final AI demonstration, preload and test an actual permitted local model on the demonstration hardware.

### Minimum records

| Record | Required fields |
| --- | --- |
| Well | ID, display name, coordinates, field, provenance, elevation/datum |
| Survey | well ID, station MD, inclination, azimuth, derived TVD/easting/northing, CRS |
| Formation interval | well ID, canonical formation, MD/TVD interval, datum, method, uncertainty |
| Document | ID, hash, original filename, stored path, page count, provenance, ingestion status |
| Event | ID, well ID, event type, interval/reference, formation, observations, cause, mitigation, outcome, sources, review state |
| Source reference | document ID, page, excerpt, optional bounding box, extraction method, field provenance |
| Telemetry frame | well ID, source ID, timestamp, sequence, operation, typed readings/units, quality flags |
| Alert | ID, well ID, hazard, state, severity, basis, evidence IDs, model/rule version, timestamps, freshness |
| Decision | alert ID, actor, acknowledgement/note, timestamp, evidence snapshot |

Keep extraction confidence, analogy strength, signal quality, model score, and operational severity distinct. A number labeled probability must be backed by calibration evidence; otherwise call it a score.

### API additions and corrections

Freeze precise response schemas before parallel UI/backend work. Extend existing `/api/v1` conventions:

- `GET /wells/{id}/nearby?radius_km=...`: validated radius, distances, candidate list; 404 for unknown active well.
- Correct `GET /wells/{id}/trajectory` and `/formations`: well-specific records and provenance.
- `GET /events`: query, formation, type, well, depth-reference filters, pagination.
- `POST /documents`: multipart upload returning persisted ingestion job ID.
- `GET /documents/{id}` and `/pages/{page}`: metadata and actual page/source.
- `GET /ingestion-jobs/{id}` and `PATCH /events/{id}/review`: status and recorded corrections.
- `GET /correlations`: active/offset IDs, alignment method, comparable intervals, uncertainty and exclusions.
- Extend risks routes with alert history and explicit acknowledgement/decision persistence.
- Extend assistant route with well/formation/evidence context and structured citations.
- Demo-only session create/reset/play/pause/seek endpoints, disabled outside demo profile.

Use existing polling initially if it is adequate; websocket delivery must add reconnect, deduplication, and source freshness if adopted. Do not calculate a new alert identity on every poll.

## 7. Correlation, risk, and grounded intelligence

### Matching order

1. Surface-radius filter identifies nearby candidates using real coordinates.
2. Validate survey CRS and vertical datums before subsurface distance calculations.
3. Match canonical formation and interval coverage.
4. Align within formation using documented tops; express uncertainty.
5. Rank evidence by relevant event, geological support, location, recency where meaningful, and data quality.
6. Show the factors and exclusions in the UI.

Minimum prototype correlation is formation-top-relative mapping, explicitly labeled approximate. Do not equate equal offsets below the formation top with a confirmed geological horizon. Missing tops must produce “insufficient correlation data.” Add constrained log alignment only after independent checks show it improves the baseline.

Never calculate Euclidean 3D distances with longitude/latitude degrees as horizontal units and metres as vertical units. Convert to an appropriate projected/local metric frame first, document the datum, and test known separations.

### Two separate warning mechanisms

**Historical approach watch:** a relevant approved historical event lies ahead in an aligned interval. This can work while live parameters are normal. Show interval, distance, uncertainty, supporting wells, source references, and data quality.

**Telemetry anomaly warning:** a recent window shows interpretable adverse signals or model output. Show observed changes and baseline window. Historical evidence enriches the warning; lack of historical evidence must not suppress a strong live signal.

Acknowledge does not equal resolve. Add hysteresis, event deduplication, operation-aware suppression, and a stale-data state. Scope windows by well and replay session. Out-of-order samples and repeated packets must not create phantom trends.

### Actual AI/ML, with defensible claims

- Retain transparent rules as a baseline, with their method named in the API and UI.
- Train one real experimental classifier if suitable labeled data exists; save preprocessing, feature order, artifact hash, dataset version, and evaluation report.
- If only synthetic data exists, describe it as synthetic workflow validation, not evidence of field predictive accuracy.
- Split by well/scenario and time, not randomly across overlapping windows. Prevent incident labels and future samples from leaking into features.
- Measure event recall, false alerts per operating hour, precision, lead time distribution, and missed events; compare against rules.
- Do not require LSTM merely because it appears in the deck. Implement it only with sufficient sequence data and a measurable benefit; report its deferred status honestly otherwise.
- Define the alert horizon and incident onset before evaluating. The warning must precede labeled onset to count as predictive.
- Validate physics inputs, units, and assumptions independently. A physics calculation is supporting context, not proof of safety.

### Retrieval and answer grounding

- Search approved event records plus exact source excerpts; preserve document/page IDs during chunking.
- Retrieve using geological filters before semantic ranking; do not reward unrelated wells for similar raw MD.
- LLM receives only bounded context and treats report text as data, not instructions.
- Reject nonexistent citation IDs, and verify that factual claims are supported by the cited passage.
- Never invent a source, mitigation outcome, equipment limit, or operating setpoint when evidence is absent.
- A failed model call returns source search plus an availability message, not a fabricated answer.

## 8. Verification and release criteria

These are target gates, not current measurements.

### Functional checks

- Clean checkout starts with documented commands; UI production build and API smoke tests pass.
- Radius boundaries, invalid input, zero matches, and regional analogue separation are tested.
- Selecting an offset changes the survey, formations, and evidence; invalid IDs return 404.
- Text and scanned PDFs produce verifiable pages and extraction results; ambiguous fields remain reviewable.
- Duplicate document upload is idempotent; failed extraction remains visible and retryable.
- Every showcased citation resolves to a real document/page and supporting excerpt.
- Formation-relative mapping passes fixtures with deliberately different formation depths and datums.
- Historical watch occurs before synthetic interval entry; telemetry warning occurs at the defined replay condition.
- Normal-operation and missing-sensor controls do not produce unsupported confident warnings.
- No telemetry, alert, or chat context crosses well/session boundaries.
- Replay reset clears scenario state and yields the same event sequence on repeated runs.
- Decision and review state survive restart.
- Unsupported questions abstain; model-unavailable state remains useful.
- Internet-disconnected run retains maps, fonts, sources, search, replay, and the preloaded local model where claimed.

### Performance targets on recorded hardware

- Warm nearby-well and event searches: p95 under one second on the demo corpus.
- Replay sample-to-visible-warning: p95 under two seconds; record ingestion, compute, and presentation timestamps separately.
- Smooth interaction at 1366×768 and the capture resolution; no unbounded telemetry arrays.
- Measure OCR and local model latency and publish hardware/context. Do not promise arbitrary latency before measuring.

### Evaluation assets

Add a small manually checked extraction gold set, expected search results, correlation fixtures, and scenario event onsets. Report denominators and errors, not just percentages. Synthetic evaluation cannot establish reduced field NPT, prevented blowouts, or operational deployment readiness.

## 9. Repository presentation after implementation

Rewrite the README only after the baseline runs. Recommended opening:

> StrataSentry NWIS turns historical drilling reports into formation-aware, source-linked warnings for active wells. Built for SIH 2026 Problem Statement 26121, alongside Oil India's eRTMAC.

Then: video thumbnail and link; one annotated screenshot; three proof points; quickstart; current capability table; synthetic data disclosure; architecture actually running; evaluation results; limitations; team and submission.

Replace inflated production and security assertions with observed capabilities. Keep future architecture separate from the prototype architecture. Use the canonical Fadhil006 repository URL in new public documentation; the submitted PDF contains an older repository link and should not be silently rewritten as if it were the original submission.

Use ordinary, descriptive commits such as `fix(api): isolate replay state by well` or `feat(evidence): link events to source pages`. No fabricated work history, metrics, or deployment claims. Publish the film and its caption/transcript assets with a reproducible release; keep large render artifacts out of normal Git history.

## 10. Decisions still needed

Proceed with stated defaults; these do not block parallel implementation after approval.

| Question | Default until confirmed |
| --- | --- |
| Official video duration/file-size constraints? | 180-second master; reusable 90-second cut |
| Real OIL data or interface documentation available? | Fully labeled synthetic corpus and read-only replay adapter |
| Demonstration hardware? | Laptop-local baseline; model chosen after RAM/VRAM measurement |
| Narration language and speaker? | Clear English human narration; English captions |
| Existing product name retained? | StrataSentry NWIS; NWIS expansion corrected |
| Who validates petroleum terminology and synthetic events? | Team obtains domain review before recording claims |
| Remote/publishing destination? | Canonical repo is Fadhil006/Oil_India; current local origin still points to AbhiKamp/Oil_India |

## References used in this plan

- User-provided PS 26121 and the six-page submitted presentation.
- Repository source paths cited in the assessment above.
- [Official Remotion skills](https://github.com/remotion-dev/skills) and [installation documentation](https://www.remotion.dev/docs/ai/skills).
- [OpenCode skill discovery](https://opencode.ai/docs/skills/): project `.agents/skills/` is supported.

The official `remotion-best-practices` skill and its referenced guides are installed project-locally under `.agents/skills/remotion-best-practices/`; `skills-lock.json` records the source/hash. Restart OpenCode to discover it. Installation does not create a video project or install the Remotion renderer into the app.
