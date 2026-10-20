# Browser checks

Use a running production dashboard and a local API. Install the isolated capture/test dependencies with `npm ci` in `apps/video`; the production dashboard does not need Playwright. These checks currently use `/usr/bin/chromium`.

```bash
node tests/browser/local-only.mjs
node tests/browser/stale-context.mjs
```

Set `NWIS_DASHBOARD_URL` if the dashboard is not at `http://127.0.0.1:41987`.

The dashboard starts/reset its synthetic replay on load. To avoid touching an ongoing demo, start a separate real API instance:

```bash
NWIS_DATA_DIR=/tmp/nwis-browser-check uvicorn apps.api.app.main:app --host 127.0.0.1 --port 18001
NWIS_TEST_API_URL=http://127.0.0.1:18001 node tests/browser/local-only.mjs
NWIS_TEST_API_URL=http://127.0.0.1:18001 node tests/browser/stale-context.mjs
```

- `local-only.mjs` blocks non-loopback browser requests and exercises real nearby-well filtering and source viewing. The optional API target is a separate **real** local process, not a canned API response. This is a browser-egress check, not certification of an air-gapped deployment.
- `stale-context.mjs` deliberately mocks/delays the assistant response, switches well contexts, and verifies that stale content is discarded. Its synthetic answers are test fixtures, **not application footage or model output**.

Real filming scripts live under `demo/capture/`. Do not use mocked response footage to demonstrate product capabilities.
