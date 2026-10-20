# Project instructions — StrataSentry NWIS

## Project context

- SIH 2026, Oil India Limited, problem statement 26121; Healix 1 (team 172547).
- NWIS means **Nearby Wells Intelligence System**. It is a read-only decision-support concept beside eRTMAC, not a rig-control system.
- Canonical repository: https://github.com/Fadhil006/Oil_India. The local `origin` was still configured as `AbhiKamp/Oil_India` at initialization; inspect it before pushing.
- The submitted presentation is `Healix-1_SIH-2026_PS-26121_Submission.pdf` at repository root. Do not confuse it with the synthetic report in `demo/`.
- Start new implementation work with `docs/prototype-plan.md`, `docs/video-plan.md`, and `docs/implementation-handoff.md`. These are plans, not descriptions of implemented features.

## Repository layout

- `apps/api/`: FastAPI gateway (`app/main.py`), route handlers, schemas, and an orchestrator bridging domain services.
- `apps/dashboard/`: Next.js 14 / React 18 / TypeScript UI; `app/` contains the entry page and styles, `components/` contains operations panels. The page currently imports `lib/api` and `lib/types`, but `lib/` is absent in this checkout.
- `services/`: document extraction, telemetry, geometry, formation correlation, risk, physics, retrieval, and fusion implementations. Directories use hyphens; some API imports use underscore names. `scripts/link_services.py` is Windows-specific. Check packaging before assuming the API starts on Linux.
- `data/synthetic/`, `data/schemas/`, `demo/`: synthetic wells, surveys, telemetry, reports, schemas, and demo assets. Synthetic data is not OIL field data.
- `models/`: model training/evaluation scripts; some runtime model code currently uses heuristic stand-ins. Do not describe these as validated trained models.
- `database/`, `infrastructure/`, `monitoring/`, `security/`: SQL/configuration and supporting modules. README architecture includes intended deployment components, not all proven running services.
- `tests/` plus `apps/api/tests/` and service-local `tests/`: integration, API, domain, and performance checks.
- `docs/`, `architecture/`: system documentation, planning documents, and diagrams.
- `.agents/skills/remotion-best-practices/`: upstream Remotion video-production guidance; source recorded in `skills-lock.json`. Restart OpenCode to discover the newly installed skill. No video application has been created yet.

## Existing conventions and constraints

- Preserve existing functionality, inspect affected services and tests, and make targeted changes.
- `CONTRIBUTING.md` calls for PEP 8, `black --line-length 100`, `flake8`, `mypy --ignore-missing-imports`, functional typed React components, disposal of Three.js resources, reproducible datasets/models, and unit checks for extraction, geometry, and physics. These are repository guidance, not verified passing checks.
- Keep engineering measurements explicit about units, depth reference (MD versus TVD), source document/page, and synthetic versus observed status. Avoid unsupported operational recommendations or confident risk probabilities.
- Keep local secrets in `.env` files (ignored); use `.env.example` for documented settings. Do not commit rendered video binaries or generated local graph caches by default.
- Do not claim production eRTMAC connectivity, air-gapped operation, OCR, or ML performance until tested on the actual implementation.
- Do not rewrite or replace the submitted PDF without explicit instruction. Use accurate team identity and repository URL in new materials.

## Commands and verified status (20 October 2026)

From the repository root unless stated otherwise:

| Command | Purpose | Verified result here |
| --- | --- | --- |
| `python -m pip install -r apps/api/requirements.txt` | Install API/test dependencies | Documented in README/Makefile; not run |
| `npm ci` in `apps/dashboard` | Install locked dashboard dependencies | Suggested clean install; not run |
| `pytest services/ tests/ apps/api/tests/ -v` | Repository test suite | Attempted; `pytest: command not found` (dependencies not installed) |
| `npm run build` in `apps/dashboard` | Production UI build | Attempted; `next: command not found` (node dependencies not installed) |
| `python scripts/seed_database.py` | Seed the synthetic database | Present in README/Makefile; not run |
| `uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload` | Local API | Present in README/Makefile; not run; packaging problem noted above |
| `npm run dev` in `apps/dashboard` | Local dashboard | Documented; not run |
| `python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff` | Synthetic telemetry | Documented; not run |
| `docker-compose up -d --build` | Intended container stack | Makefile target; not verified |

Local tool versions observed: Python 3.14.7, Node 26.8.1, npm 11.19.0. README claims Python 3.12 and Node 18+ as targets; compatibility has not been established by these checks. If startup fails, reproduce before changing architecture.

## Code graph from `/init`

On 20 October 2026, `graphify extract . --code-only` succeeded and wrote `graphify-out/graph.json` (1,080 nodes, 1,558 edges, 92 communities), plus analysis, manifest, and cache files. Graphify skipped non-code input and reported five SQL files with no extracted nodes because `tree_sitter_sql` is not installed. `graphify-out/` is local and git-ignored. No hooks, watchers, or background refreshes were configured. Do not run Graphify as part of ordinary development requests; reserve it for a user-invoked `/init`.
