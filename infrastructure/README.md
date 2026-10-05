# Infrastructure & Deployment Automation

This directory contains containerization definitions, message broker configs, database initialization, and air-gapped rig-site edge node daemons.

---

## Subdirectories

- **`docker/`**:
  - `Dockerfile.api`: Python 3.12 container for FastAPI backend.
  - `Dockerfile.dashboard`: Node.js 20 container for Next.js Tactical HUD.
  - `Dockerfile.services`: Streaming telemetry generator container.
- **`kafka/`**:
  - `init-topics.sh`: Initializes `rig.telemetry.raw`, `rig.telemetry.standardized`, and `rig.alerts.immediate`.
- **`postgres/`**:
  - `pg_hba.conf`: Host-based authentication rules for database clusters.
- **`qdrant/`**:
  - `config.yaml`: Vector engine configuration.
- **`edge-node/`**:
  - `rig_edge_daemon.py`: Autonomous edge synchronization daemon.
  - `stratasentry-edge.service`: Systemd service unit for ruggedized edge servers.
