# StrataSentry NWIS dashboard

Next.js 15 / React 18 / TypeScript interface for the local read-only NWIS prototype.

## Run

Start the API from the repository root as described in the [main README](../../README.md), then:

```bash
npm ci
npm run dev
```

Default API: `http://localhost:8000`. Set `NEXT_PUBLIC_API_URL` before building if it differs. Local development API CORS permits loopback origins; production origins must be configured explicitly.

For browser capture, use a stable production build rather than building into a running dev server's `.next/` directory:

```bash
npm run build
npm run start -- --hostname 127.0.0.1 --port 41987
```

## Views

- **Operations:** real coordinate-radius filtering on a schematic map, source-backed formation comparison, historical-context watch, and explicit synthetic telemetry replay.
- **Knowledge & review:** PDF upload, extraction inspection, source viewing, and approval/rejection. The API also supports corrections with a recorded reviewer audit.
- **Handover:** engineer notes linked to an approved historical event; the active-well and historical-well identities remain distinct.

All supplied scenarios are synthetic. A source-text marker is not a physical PDF page. Top-relative mapping is approximate, model scores are uncalibrated, and the source-summary assistant is not a language model. Unknown readings remain unavailable instead of being filled with plausible values.

The coordinate schematic is not a tiled basemap; the local profile does not include a validated multi-well reservoir reconstruction. No eRTMAC connection or rig-control action is represented.

## Checks

```bash
npm run build
npm audit --audit-level=high
```

See [delivery status](../../docs/delivery-status.md) for verified commands and limits. Browser capture/check tooling is isolated from the production UI under `apps/video/` and `demo/capture/`.
