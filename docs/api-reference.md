# StrataSentry-NWIS API Reference
## RESTful & WebSocket Endpoint Specifications

Base URL: `http://localhost:8000` (or `https://<edge-host>:8000`)
OpenAPI UI: `http://localhost:8000/docs`

---

## 1. Wells & Wellbore Geometry

### `GET /api/v1/wells`
Returns a list of all active and offset wells with surface coordinates and basin metadata.

**Response `200 OK`**:
```json
[
  {
    "well_id": "NHK-421",
    "well_name": "Naharkatiya 421",
    "field": "Naharkatiya",
    "basin": "Assam-Arakan",
    "status": "DRILLING_ACTIVE",
    "surface_latitude": 27.2842,
    "surface_longitude": 95.3418,
    "spud_date": "2026-09-12",
    "current_depth_md": 2845.5,
    "target_depth_md": 3950.0
  }
]
```

### `GET /api/v1/wells/{well_id}/trajectory`
Returns the 3D Minimum Curvature calculated trajectory stations (MD, Inc, Azi, TVD, Northing, Easting, DLS).

### `GET /api/v1/wells/{well_id}/formations`
Returns penetrated and prognosed stratigraphic formation tops with depths and rock lithologies.

---

## 2. Real-Time Telemetry & Streaming

### `GET /api/v1/telemetry/{well_id}/latest`
Returns the most recent 1 Hz telemetry sensor frame.

**Response `200 OK`**:
```json
{
  "timestamp": "2026-10-05T17:35:12.450Z",
  "well_id": "NHK-421",
  "measured_depth": 2845.2,
  "bit_depth": 2845.0,
  "rop": 12.4,
  "wob": 14.2,
  "surface_torque": 18.5,
  "rotary_rpm": 110,
  "standpipe_pressure": 3150.0,
  "flow_in": 2400.0,
  "flow_out_pct": 74.2,
  "pit_volume": 42.1,
  "mud_weight_in": 1.28,
  "ecd": 1.34,
  "gamma_ray": 84.5
}
```

### `WS /ws/telemetry`
High-speed bidirectional WebSocket stream broadcasting live telemetry packets and immediate risk alerts at up to 10 Hz.

---

## 3. Risk Assessment & Alerts

### `GET /api/v1/risks/{well_id}/current`
Evaluates and returns the instantaneous fused risk assessment across ML models and physics gates.

**Response `200 OK`**:
```json
{
  "well_id": "NHK-421",
  "measured_depth": 2845.2,
  "overall_severity": "WARNING",
  "lead_time_seconds": 960,
  "primary_hazard": "HOLE_PACKOFF",
  "ml_probabilities": {
    "normal": 0.12,
    "hole_packoff": 0.78,
    "differential_sticking": 0.06,
    "gas_kick": 0.03,
    "lost_circulation": 0.01
  },
  "physics_factors": {
    "annular_pressure_loss_psi": 420.5,
    "cuttings_loading_pct": 7.8,
    "torque_drag_friction_factor": 0.38,
    "mse_ksi": 84.2
  },
  "recommendations": [
    "Stop drilling ahead immediately",
    "Pick up string off bottom to 2,835m MD",
    "Circulate at 2,400 LPM with low rotary speed (40 RPM)",
    "Inspect shaker screens for splintery Barail coal cavings"
  ]
}
```

### `GET /api/v1/risks/{well_id}/alerts`
Fetches historical alerts and driller acknowledgments for the specified well.

---

## 4. Depth-Aware RAG Copilot & Document Intelligence

### `POST /api/v1/assistant/chat`
Ask natural language questions grounded in offset well completion reports and historical mudlogs.

**Request**:
```json
{
  "well_id": "NHK-421",
  "current_depth": 2845.0,
  "query": "What stuck pipe incidents occurred in Barail coal around 2850m in offset wells and how were they freed?"
}
```

**Response `200 OK`**:
```json
{
  "answer": "In offset well MOR-118 at 2,848.0m MD within the Barail Coal-Shale sequence, the drillstring suffered mechanical hole pack-off due to coal seam sloughing during a connection. The pipe was successfully freed after 4.5 hours by pumping a high-viscosity pill (45 bbls), reducing pump rate to 1,600 LPM, and jarring upward with 80 klbs overpull.",
  "citations": [
    {
      "well_name": "MOR-118",
      "wcr_section": "Section 4: Drilling Problems & Fishing Operations",
      "depth_interval_md": "2835.0 - 2860.0 m",
      "formation": "Barail Coal-Shale",
      "page_number": 19,
      "confidence": 0.96
    }
  ]
}
```

### `POST /api/v1/documents/upload`
Uploads a legacy WCR or mudlog PDF for automated extraction and vector embedding.
