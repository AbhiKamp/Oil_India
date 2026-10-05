# StrataSentry-NWIS Tactical Drilling Operations HUD

Next.js / React interactive tactical driller cabin and operations center display for real-time hazard monitoring, 3D wellbore geometry, and AI assistant interaction.

---

## Features

- **3D Wellbore Spatial Viewer**:
  - Interactive Canvas / WebGL 3D borehole trajectory viewer.
  - Real-time bit position tracking.
  - Sub-surface geological formation horizon planes (Dihing, Tipam, Girujan, Barail, Kopili).
  - Offset well trajectories (e.g. MOR-118, NHK-412).
- **Live Drilling Gauges & Telemetry Panel**:
  - High-frequency digital indicators: ROP, WOB, RPM, Torque, SPP, Flow In, Flow Out %, Pit Volume, Dynamic ECD, Gamma Ray.
- **Multi-Modal Risk & Hazard Alerts**:
  - Severity status badges (`CRITICAL`, `WARNING`, `WATCH`, `INFO`).
  - Estimated lead-time countdowns.
  - Actionable step-by-step Standard Operating Procedures (SOPs).
- **Historical Evidence Drawer**:
  - Grounded offset well completion report excerpts with exact page and depth citations.
- **Interactive AI Drilling Copilot**:
  - Conversational RAG assistant grounded in legacy well archives.

---

## Running Locally

```bash
cd apps/dashboard
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.
