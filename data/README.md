# StrataSentry-NWIS Data Directory

This directory contains schemas and synthetic datasets representing exploratory and development drilling operations in the **Assam-Arakan Basin** (Upper Assam Shelf).

---

## 1. Directory Structure

- **`schemas/`**: Strict JSON schemas defining data structures for:
  - `drilling_event.schema.json`: Hazardous events (stuck pipe, kick, losses)
  - `telemetry.schema.json`: 1 Hz / 10 Hz MWD/LWD real-time sensor packets
  - `well_trajectory.schema.json`: Directional surveys (Minimum Curvature Method)
  - `risk_alert.schema.json`: Unified advisory alerts dispatched to drillers
- **`synthetic/`**:
  - `wells/wells.json`: Metadata for active well NHK-421 and offsets NHK-412, MOR-118, BGH-07.
  - `reports/`: Text excerpts mimicking historical Well Completion Reports (WCRs) with detailed pack-off, kick, and loss incidents.
  - `telemetry/`: High-frequency streaming telemetry CSV with induced annular pack-off anomaly.
  - `surveys/`: 3D directional surveys (MD, Inclination, Azimuth, TVD, Northing, Easting, DLS).
  - `well_logs/`: Depth-indexed petrophysical logs (GR, Resistivity, Bulk Density, Sonic DT).
