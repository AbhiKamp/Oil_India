# Implementation handoff and delivery gates

Read [prototype plan](prototype-plan.md) and [video plan](video-plan.md) first.

This is a future execution brief. The current task is planning only. Implementation begins after the team approves it.

## 1. Team operating model

Use six implementation workstreams and one integration owner. Parallelism is useful after contracts and the demonstration scenario are frozen. More agents do not compensate for incompatible schemas or inconsistent story data.

Use isolated branches/worktrees. Each owner returns a bounded patch, checks run, screenshots or sample responses where relevant, and remaining limitations. The integration owner owns shared contracts and merges; owners do not change each other's files without coordination.

The video owner starts with the first wave, producing a paper edit and scratch track while the application is repaired. Film quality gets reserved time, not leftover time.

### Suggested effort allocation

Reserve roughly 25% for the film, capture, narration, and comprehension testing; 20% for evidence/ingestion; 20% for integrated UI; 15% for geospatial/correlation; 10% for risk/replay; and 10% for integration/release checks. Adjust after the baseline audit. These are planning allocations, not delivery-time guarantees.

## 2. Dependency graph

```text
A: baseline + contracts + scenario vocabulary
├── B: documents + source-linked events
├── C: geospatial + formation correlation
├── D: replay + risk lifecycle
├── E: dashboard shell against shared contracts
└── F: film paper edit + styleframes

B + C → historical approach watch and grounded retrieval
B + C + D + E → complete evidence-to-decision workflow
Complete workflow → deterministic capture → F final edit
Integrated tests + offline check + comprehension test → release
```

Do not start six agents implementing separate versions of the same data model. Freeze contracts in the first wave, then distribute narrow responsibilities.

## 3. Work packages

### A — Integration owner: runnable baseline and contracts

**Existing paths:** `apps/dashboard/package.json`, `apps/dashboard/app/page.tsx`, `apps/api/app/main.py`, `apps/api/app/schemas/`, `apps/api/app/services/orchestrator.py`, `scripts/link_services.py`, `Makefile`, `scripts/`, `data/schemas/`.

**Proposed paths:** `apps/dashboard/lib/`, `demo/scenarios/`, compact shared contract documentation under `docs/`.

Tasks:

1. Reproduce and record startup/build failures from a clean checkout.
2. Fix missing dashboard API/types modules based on actual route schemas.
3. Normalize Python package imports portably; do not preserve the Windows junction deletion behavior. Inventory all underscore/hyphen callers before selecting a rename or packaging approach.
4. Establish one local persistent store and per-well/session state. Preserve useful domain implementations.
5. Freeze field names, units, null semantics, error shapes, event/source IDs, and demo scenario version.
6. Provide one documented demo startup and reset workflow plus readiness checks.
7. Coordinate corrections to README claims once verified.

**Exit:** API health and UI load from a clean checkout; production UI build passes; a valid active well can be selected; agreed contract examples and scenario vocabulary are available.

**Do not:** redesign the service ecosystem, add unrelated authentication portals, or make optional infrastructure mandatory.

### B — Evidence owner: documents, extraction, retrieval

**Existing paths:** `services/document-intelligence/`, `services/rag-engine/`, `apps/api/app/routes/documents.py`, `apps/api/app/routes/assistant.py`, `data/synthetic/reports/`, relevant database definitions.

Tasks:

1. Inventory existing parser/OCR/extractor code; remove fake binary-string “PDF extraction” from successful paths.
2. Add persistent upload jobs and page-level source records, including actual scanned-page OCR.
3. Extract normalized event records without fabricating absent fields; keep original wording and units.
4. Implement review/correction, document deduplication, and safe file handling.
5. Implement filtered search with real citations and unsupported-answer abstention.
6. Integrate an actual local model for the final AI path; label evidence-only fallback clearly.
7. Deliver an authored synthetic corpus and independently checked extraction gold set.

**Exit:** a new PDF ingests through the UI/API, becomes a searchable reviewed event, survives restart, and opens its correct source page. Scanned and ambiguous examples pass. A question with no support does not produce a made-up citation.

**Contract dependencies:** event/source schemas from A; formation IDs from C. Do not own dashboard components; supply responses and fixtures to E.

### C — Spatial owner: nearby wells and geological relevance

**Existing paths:** `services/well-geometry/`, `services/formation-correlation/`, `apps/api/app/routes/wells.py`, `apps/api/app/routes/trajectory.py`, `data/synthetic/wells/`, `data/synthetic/surveys/`.

Tasks:

1. Validate coordinates, radius calculations, projected survey positions, and vertical datums.
2. Provide different trajectories/tops for different wells and unknown-well errors.
3. Implement nearby candidates and explicitly separate regional analogues.
4. Implement formation-relative interval mapping with uncertainty and explanations.
5. Supply aligned event intervals and match/exclusion factors to risk and UI owners.
6. Verify interpolation and geometry with analytic fixtures. Add DTW only after the top-based baseline is correct.

**Exit:** radius changes yield expected candidates; differing raw depths align in the intended formation; inappropriate or missing-data matches are excluded or flagged. Known geometry checks pass.

**Do not:** use fabricated paths, mix degrees and metres, or market a top-relative approximation as precise geological reconstruction.

### D — Risk owner: replay, signals, and alert lifecycle

**Existing paths:** `scripts/simulate_telemetry.py`, `scripts/run_historical_replay.py`, `services/telemetry-ingestion/`, `services/risk-engine/`, `services/risk-fusion/`, `services/physics-validation/`, `models/`, API telemetry/risk/stream routes.

Tasks:

1. Build deterministic timestamped replay sessions with play/pause/seek/reset and isolated state.
2. Separate historical approach watch from live telemetry anomaly warning.
3. Use approved event intervals from B/C for actual historical watch computation.
4. Add quality handling, operation context, hysteresis, deduplication, and persistent alert/decision lifecycle.
5. Label heuristic baseline honestly; add one real experimental trained model with saved evaluation/artifact if data permits.
6. Evaluate normal controls, pack-off, kick, stale/missing sensors, repeated samples, and well switching.
7. Publish lead-time and false-alert results with synthetic-data limitations.

**Exit:** resettable hero replay, second kick scenario, quiet normal control, source-linked historical warning before interval entry, and interpretable telemetry escalation. Acknowledgement does not clear observed risk.

**Do not:** let the UI script severity changes, require historical evidence to emit a strong telemetry warning, or turn interval ETA into an incident countdown.

### E — Product owner: integrated interface

**Existing paths:** `apps/dashboard/app/`, `apps/dashboard/components/`, restored `apps/dashboard/lib/`.

**Proposed component areas:** nearby map, formation comparison, document review, decision history, replay controls.

Tasks:

1. Implement the restrained mission-control visual system and responsive shell.
2. Build accessible map/radius/list interaction using a suitable maintained map renderer; bundle local geographic assets for the demo and preserve required attribution.
3. Replace procedural offset paths with actual supplied surveys; reuse installed Three.js where it helps.
4. Build formation comparison, source viewer/review, evidence search, and decision flow.
5. Keep map, selection, evidence, charts, replay, and assistant context synchronized.
6. Surface loading, empty, unavailable, stale, and low-confidence states explicitly.
7. Provide stable capture selectors and camera presets; no filming-only fake business logic.

**Exit:** a complete keyboard-usable golden path at 1366×768 and 1920×1080, real API interactions, no fabricated connection badges or hard-coded event outcomes.

**Library policy:** inspect existing dependencies first. No whole-stack upgrade for styling. Verify maintained versions/security before installing any map/PDF/capture dependency; use official docs at implementation time.

### F — Film owner: narrative, capture, edit, delivery

**Inputs:** `docs/video-plan.md`, canonical scenario, integrated app, installed Remotion skill.
**Proposed paths:** `apps/video/`, `demo/capture/`, `docs/media/`.

Tasks:

1. Produce paper edit, scratch narration, three styleframes, and asset/license list immediately.
2. Create a real app-footage shot checklist with E; identify required capture states early.
3. Build Remotion composition in a separate workspace after implementation approval.
4. Replace storyboard placeholders with actual app recordings tied to a revision/scenario.
5. Direct narration and original/licensed score; create captions and readable explanatory overlays.
6. Conduct one-view comprehension testing and revise the cut based on misunderstood concepts.
7. Deliver master, short cut, transcript/captions, thumbnail, uncut walkthrough, render manifest, and credits.

**Exit:** all V0–V5 gates in the film plan pass; viewers understand the evidence-to-decision chain; each apparent product behavior exists in the app.

**Do not:** create a fake product inside the video workspace or spend the opening on a long cinematic logo animation.

## 4. Milestones and integration gates

| Gate | Required evidence | Blocks |
| --- | --- | --- |
| G0: scope freeze | Canonical story, schemas, dataset labels, ownership, video length assumption | Parallel domain implementation |
| G1: runnable baseline | Clean-checkout startup, UI build, API health, typed client | Integrated UI and capture |
| G2: evidence chain | Upload → reviewed event → search → actual page | Credible alert and assistant |
| G3: spatial chain | Radius query → valid candidate → formation alignment → comparable interval | Historical approach warning |
| G4: operational chain | Deterministic replay → historical watch → telemetry escalation → saved decision | Real-footage rough cut |
| G5: AI and robustness | Actual model/provider status, evaluation, normal controls, disconnected run | Final claims freeze |
| G6: film comprehension | Four of five fresh viewers explain the complete story | Final render approval |
| G7: release | Build/tests, fresh install, working media links, matching docs and claims | Submission |

### Critical path

Packaging/contracts → source-backed events → valid formation mapping → historical approach watch → integrated evidence/decision UI → actual capture → comprehension revision → final render.

Experimental model work, supplemental 3D polish, and architecture diagrams must not block this path. If time contracts, cut extra scenarios/visual polish before sacrificing source traceability or the map/correlation workflow. Keep a visibly honest capability table for any deferred P1 work.

## 5. Testing responsibilities

Use existing tests where meaningful; inspect them before trusting their assertions. Add targeted tests around business invariants rather than snapshots of implementation details.

- A owns clean-checkout setup, API contracts, persistence, and integration checks.
- B owns extraction gold set, correct pages, idempotency, citation support, and abstention.
- C owns radius edges, datum/unit handling, survey interpolation, and correlation cases.
- D owns event timing, per-well state, replay determinism, false-alert controls, and artifact evaluation.
- E owns browser golden path, accessibility basics, synchronization, and visible error states.
- F owns rendering determinism, export inspection, caption timing, asset rights, and comprehension.

Known repository command to reassess after startup repair: `pytest services/ tests/ apps/api/tests/ -v`. Frontend production check: `npm run build` within `apps/dashboard`. Add the smallest runnable browser check for the end-to-end golden path. Record actual commands/results; do not report tests that were not run.

## 6. Assignment prompt template

> Read docs/prototype-plan.md, docs/video-plan.md, and your work package in docs/implementation-handoff.md. Implement only the assigned package using the frozen contracts and canonical scenario. Inspect existing code first, preserve unrelated changes, and coordinate any shared-schema change through the integration owner. Use real source-linked data, explicit synthetic labels, and truthful method/status reporting. Verify your acceptance criteria with runnable checks and report changed paths, commands/results, sample outputs or screenshots, and remaining limitations. Do not claim production integration or validated field prediction. Do not edit other owners' areas or commit unrelated files.

For F, append:

> Load the installed remotion-best-practices skill. Build the film from actual app footage and clearly labeled explanatory visuals. Optimize first for single-view comprehension, then cinematic polish. Follow the shot table and V0–V5 review gates; keep original footage and an asset/claim manifest.

## 7. Release checklist

- [ ] Correct Nearby Wells Intelligence System naming everywhere public.
- [ ] Team 172547 / Healix 1 / PS 26121 consistent.
- [ ] Canonical repository URL is Fadhil006/Oil_India.
- [ ] Current origin reviewed before any push; never push to the old repository accidentally.
- [ ] Submitted PDF preserved under its descriptive filename; internal original links not silently altered.
- [ ] Clean-checkout instructions verified on the actual demo machine.
- [ ] Local map/model/document assets preloaded and disconnected operation exercised.
- [ ] Synthetic vs measured vs proposed capabilities clearly distinguished.
- [ ] Citation/page checks and scenario consistency review complete.
- [ ] Reproducible replay and saved decisions verified.
- [ ] Video and prototype match the same revision and scenario.
- [ ] Comprehension and audio/readability gates passed.
- [ ] Large video exports published as release/media assets rather than ordinary Git blobs.
- [ ] Third-party skill/media attribution and applicable licenses preserved.
- [ ] Conventional, factual commits; no generated work history or unsupported marketing claims.

## 8. Definition of done

A judge can watch the film once, explain the problem accurately, open the application, change the radius, inspect why an offset is relevant, follow a warning to an actual historical page, and see the engineer's decision retained. The team can reproduce the same demonstration from a clean checkout and defend every claim made in the film.
