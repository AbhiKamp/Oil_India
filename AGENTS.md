# Project instructions — StrataSentry NWIS

## Project context

- SIH 2026, Oil India Limited, problem statement 26121; Healix 1 (team 172547).
- NWIS means **Nearby Wells Intelligence System**. It is a read-only decision-support concept beside eRTMAC, not a rig-control system.
- Canonical repository: https://github.com/Fadhil006/Oil_India. The local `origin` was still configured as `AbhiKamp/Oil_India` at initialization; inspect it before pushing.
- The submitted presentation is `Healix-1_SIH-2026_PS-26121_Submission.pdf` at repository root. Do not confuse it with the synthetic report in `demo/`.
- Start new implementation work with `docs/prototype-plan.md`, `docs/video-plan.md`, and `docs/implementation-handoff.md`. These are plans, not descriptions of implemented features; `docs/delivery-status.md` records the implemented local scope and limitations.

## Repository layout

- `apps/api/`: FastAPI gateway (`app/main.py`), route handlers, schemas, and an orchestrator bridging domain services.
- `apps/dashboard/`: Next.js 15 / React 18 / TypeScript UI; `app/` contains operations, source/review, and handover views; `lib/` contains typed API contracts. Its nested `.gitignore` makes `lib/` trackable despite the root Python `lib/` rule.
- `apps/video/`, `demo/capture/`, `docs/media/`: isolated Remotion composition, real browser capture tooling, transcript/asset records. Video exports belong in ignored `out/`, not normal Git history.
- `services/`: document extraction, telemetry, geometry, formation correlation, risk, physics, retrieval, and fusion implementations. Directories use hyphens; `apps/api/app/service_packages.py` registers portable underscore aliases.
- `data/synthetic/`, `data/schemas/`, `demo/`: synthetic wells, surveys, telemetry, reports, schemas, and demo assets. Synthetic data is not OIL field data.
- `models/`: legacy model scripts plus `experimental/`, a genuinely trained NumPy classifier with grouped synthetic evaluation. The runtime alert baseline still uses uncalibrated heuristics; do not describe it as trained XGBoost/LSTM or confuse synthetic model results with field validation.
- `database/`, `infrastructure/`, `monitoring/`, `security/`: SQL/configuration and supporting modules. README architecture includes intended deployment components, not all proven running services.
- `tests/` plus `apps/api/tests/` and service-local `tests/`: integration, API, domain, and performance checks.
- `docs/`, `architecture/`: system documentation, planning documents, and diagrams.
- `.agents/skills/remotion-best-practices/`: upstream Remotion video-production guidance; source recorded in `skills-lock.json`. Restart OpenCode after skill configuration changes.
- `.local/nwis/` (ignored): SQLite knowledge/review/decision store and content-addressed uploaded files. `NWIS_DATA_DIR` overrides this path; use a temporary directory in persistence tests.

## Existing conventions and constraints

- Preserve existing functionality, inspect affected services and tests, and make targeted changes.
- `CONTRIBUTING.md` calls for PEP 8, `black --line-length 100`, `flake8`, `mypy --ignore-missing-imports`, functional typed React components, disposal of Three.js resources, reproducible datasets/models, and unit checks for extraction, geometry, and physics. These are repository guidance, not verified passing checks.
- Keep engineering measurements explicit about units, depth reference (MD versus TVD), source document/page, and synthetic versus observed status. Avoid unsupported operational recommendations or confident risk probabilities.
- Keep local secrets in `.env` files (ignored); use `.env.example` for documented settings. Do not commit rendered video binaries or generated local graph caches by default.
- Do not claim production eRTMAC connectivity, air-gapped operation, OCR, or ML performance until tested on the actual implementation.
- Keep uploaded events out of operational retrieval until approved. Do not treat text-report page markers as verified physical PDF pages. Historical offset events may be linked to a decision for the active well; preserve both identities.
- Reviewer identity is self-entered in the local prototype, not authenticated. Bind the demo to loopback; do not expose the local upload/control profile publicly.
- Do not rewrite or replace the submitted PDF without explicit instruction. Use accurate team identity and repository URL in new materials.

## Commands and verified status (20 October 2026)

From the repository root unless stated otherwise:

| Command | Purpose | Verified result here |
| --- | --- | --- |
| `python -m pip install -r apps/api/requirements.txt` | Install API/test dependencies | Installed into `/tmp/opencode/oil-api-venv` during implementation; not system-wide |
| `npm ci` in `apps/dashboard` | Install locked dashboard dependencies | Run successfully; current dependency versions are in package-lock.json |
| `python -m pytest services/ tests/ apps/api/tests/ -q` | Repository test suite | Passed in the implementation environment; `pytest.ini` uses importlib mode for service directories |
| `npm run build` in `apps/dashboard` | Production UI build | Passed after restoring typed client and upgrading to Next.js 15 |
| `python scripts/seed_database.py` | Seed the synthetic database | Present in README/Makefile; not run |
| `uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000` | Local API | Started successfully; HTTP health and source/nearby/event endpoints exercised |
| `npm run dev -- --hostname 127.0.0.1 --port 41987` in `apps/dashboard` | Local dashboard | Started and inspected in Chromium; 3000 and 3010 were occupied by unrelated processes |
| `python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff --reset` | Synthetic telemetry | Deterministic generator and replay API are tested; CLI network loop is not a field-stream validation |
| `python -m models.experimental.train` | Reproduce synthetic classifier | Run; artifact and evaluation checked into `models/experimental/artifacts/` |
| `npx tsc --noEmit` in `apps/video` | Video typecheck | Passed |
| `npx remotion render src/index.ts BeforeTheNextMetre out/sample.mp4 --frames=0-299 --browser-executable=/usr/bin/chromium` in `apps/video` | Local video render | Sample rendered; system Chromium avoids the failed automatic browser download |
| `npm audit --audit-level=high` in each JavaScript app | Dependency audit | Zero reported vulnerabilities after upgrades; rerun when dependencies change |
| `docker-compose up -d --build` | Intended container stack | Makefile target; not verified |

Local tool versions observed: Python 3.14.7, Node 26.8.1, npm 11.19.0, Tesseract 5.5.3, Poppler 26.08.0. An image-only synthetic PDF passed actual OCR extraction. Compatibility on other Python/Node versions has not been established by these checks. If startup fails, reproduce before changing architecture.

## Code graph from `/init`

On 20 October 2026, `graphify extract . --code-only` succeeded and wrote `graphify-out/graph.json` (1,080 nodes, 1,558 edges, 92 communities), plus analysis, manifest, and cache files. Graphify skipped non-code input and reported five SQL files with no extracted nodes because `tree_sitter_sql` is not installed. `graphify-out/` is local and git-ignored. No hooks, watchers, or background refreshes were configured. Do not run Graphify as part of ordinary development requests; reserve it for a user-invoked `/init`.
