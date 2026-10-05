# StrataSentry-NWIS FastAPI Gateway

High-throughput asynchronous RESTful API and WebSocket broadcast server interfacing the core analytics engines with Driller HUD displays and enterprise operations centers.

---

## Quickstart

```bash
# Run standalone API server
uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation is served at `http://localhost:8000/docs`.

---

## Endpoints Summary

- **`GET /health`**: Subsystem operational health probes.
- **`GET /api/v1/wells`**: List all active and offset wells with surface coordinates.
- **`GET /api/v1/wells/{well_id}/trajectory`**: 3D Minimum Curvature directional surveys.
- **`GET /api/v1/wells/{well_id}/formations`**: Stratigraphic tops with lithology descriptions.
- **`GET /api/v1/telemetry/{well_id}/latest`**: Latest sensor frame (ROP, WOB, Torque, SPP, Flow, Pit Vol, ECD).
- **`GET /api/v1/risks/{well_id}/current`**: Current multi-domain fused risk assessment.
- **`POST /api/v1/assistant/chat`**: Grounded natural language query to historical well archives.
- **`WS /ws/telemetry`**: 1 Hz live sensor and alert streaming socket.
