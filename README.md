# StrataSentry-NWIS 🛰️🛢️
### National Well Intelligence System & Real-Time Drilling Hazard Mitigation Platform

[![System Architecture](https://img.shields.io/badge/Architecture-Distributed_Microservices-00f0ff?style=for-the-badge&logo=diagramsdotnet)](./ARCHITECTURE.md)
[![Security Classification](https://img.shields.io/badge/Security-Air--Gapped_Critical_Infrastructure-ff0055?style=for-the-badge&logo=shield)](./SECURITY.md)
[![Domain](https://img.shields.io/badge/Domain-Upstream_Petroleum_Engineering-f59e0b?style=for-the-badge&logo=target)](./docs/petroleum-engineering-basis.md)
[![License](https://img.shields.io/badge/License-Apache_2.0-10b981?style=for-the-badge)](./LICENSE)

---

## 📌 Executive Summary

**StrataSentry-NWIS (National Well Intelligence System)** is an enterprise-grade, real-time drilling hazard detection, geological correlation, and legacy well record intelligence platform built specifically for complex upstream exploration and development campaigns (including high-pressure, depleted, and structurally complex basins such as the **Assam-Arakan Basin**).

By fusing **legacy Well Completion Reports (WCR)**, **daily drilling mudlogs**, **high-frequency WITSML telemetry** (ROP, WOB, Torque, SPP, Flow, Pit Volume, ECD, Gas), **physics-based hydraulics models**, and **machine learning anomaly detectors**, StrataSentry delivers:
1. **Real-Time Hazard Early Warning**: 15–45 minute advance detection of stuck pipe incidents (differential sticking, hole pack-off, key seating), lost circulation, and kicks.
2. **Sub-Surface Lithology & Formation Correlation**: Dynamic Time Warping (DTW) and Gamma Ray/Resistivity alignment matching active drill depth against historical offset wells to predict formation tops and pore pressure ramps ahead of bit.
3. **Physics-Constrained AI Advisory**: Real-time Bingham Plastic / Herschel-Bulkley hydraulics, dynamic ECD tracking, and soft-string torque & drag analysis coupled with XGBoost and LSTM Autoencoders.
4. **Depth-Aware RAG Copilot**: High-precision vector retrieval (Qdrant) indexing decades of unstructured drilling reports with exact offset well name, formation, and depth citations.
5. **Air-Gapped Edge Deployment**: Capable of zero-internet, autonomous execution directly on remote rig-site edge computing hardware with cryptographic synchronization to headquarters.

---

## 🏛️ System Architecture Overview

```
                      +------------------------------------------+
                      |         RIG SITE SENSORS & MWD/LWD       |
                      +------------------------------------------+
                                           |
                                [WITSML 1.4.1 / 2.0 / MQTT]
                                           v
+-----------------------+     +--------------------------+     +-------------------------+
|   LEGACY WELL DATA    |     |   TELEMETRY INGESTION    |     |  WELL GEOMETRY & TRAJ   |
| PDF/Scanned WCRs,     |     | Kafka Message Bus        |     | Minimum Curvature (MCM) |
| Mudlogs, Core Data    |     | High-speed Stream Parser |     | 3D Linestring Builder   |
+-----------------------+     +--------------------------+     +-------------------------+
            |                              |                                |
            v                              v                                v
+-----------------------+     +----------------------------------------------------------+
| DOCUMENT INTELLIGENCE |     |                REAL-TIME FUSION BACKBONE                 |
| Depth/Formation/Event |     | +------------------------------------------------------+ |
| Extraction Pipeline   |     | | PHYSICS VALIDATION   | ML ANOMALY ENGINE             | |
| Confidence Evaluator  |     | | - Bingham Hydraulics | - XGBoost Risk Classifier     | |
+-----------------------+     | | - Dynamic ECD Calc   | - LSTM Multivariate AE        | |
            |                 | | - Torque & Drag      | - Dynamic Statistical Limits  | |
            v                 | +------------------------------------------------------+ |
+-----------------------+     +----------------------------------------------------------+
|  DEPTH-AWARE RAG      |                                  |
|  Qdrant Vector DB     | <--------------------------------+
|  Assam Basin Ontology |
|  Mistral Copilot      |
+-----------------------+
            \                                              /
             \                                            /
              v                                          v
      +----------------------------------------------------------+
      |               STRATASENTRY UNIFIED API & WEBSOCKET       |
      |             (FastAPI / PostGIS / TimescaleDB)            |
      +----------------------------------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+-----------------------------------+     +-----------------------------------+
|  DRILLER CABIN TACTICAL HUD       |     |  HQ ASSET MONITORING CENTER       |
|  - 3D Wellbore Trajectory Viewer  |     |  - Multi-Rig Fleet Overview       |
|  - Real-Time Dynamic Mud Gauges   |     |  - Basin-wide Offset Comparison   |
|  - Sub-minute Hazard Alerts & SOP |     |  - Legacy Evidence Audit Trail    |
|  - Grounded Drilling Copilot      |     |  - Post-Well Incident Review      |
+-----------------------------------+     +-----------------------------------+
```

Detailed architectural diagrams are available in [`architecture/`](./architecture/):
- **Technical Approach**: [architecture/technical-approach.png](./architecture/technical-approach.png)
- **Enterprise System Architecture**: [architecture/system-architecture.png](./architecture/system-architecture.png)
- **Industrial Data Pipeline Flow**: [architecture/data-flow.png](./architecture/data-flow.png)
- **Air-Gapped Rig-Site Edge Deployment**: [architecture/air-gapped-deployment.png](./architecture/air-gapped-deployment.png)
- **Relational & Timeseries Database ERD**: [architecture/database-schema.png](./architecture/database-schema.png)

---

## 📂 Repository Structure

```
STRATASENTRY-NWIS/
│
├── README.md                      # Primary project overview and quickstart
├── ARCHITECTURE.md                # System architecture, protocol specifications, data pipeline
├── SECURITY.md                    # Air-gap security, RBAC, model integrity & cryptography
├── CONTRIBUTING.md                # Developer setup, coding standards, branch rules
├── LICENSE                        # Apache 2.0 Open Industry License
├── .env.example                   # Default environment variables configuration
├── docker-compose.yml             # Full-stack composition (API, DB, Kafka, Qdrant, UI)
├── Makefile                       # One-touch build, test, seed, and run targets
│
├── docs/                          # In-depth technical and scientific documentation
│   ├── problem-statement.md       # Upstream drilling challenges & economic loss breakdown
│   ├── solution-overview.md       # Solution blueprint and capability matrix
│   ├── technical-architecture.md  # Detailed microservices, schemas, latency budgets
│   ├── deployment-architecture.md # Cloud, on-premise, and air-gapped rig-edge topologies
│   ├── data-flow.md               # Telemetry and document processing event pipelines
│   ├── ml-methodology.md          # XGBoost, LSTM AE, loss functions & calibration
│   ├── rag-methodology.md         # Depth-indexed chunking, vector retrieval & prompt grounding
│   ├── petroleum-engineering-basis.md # MCM geometry, Bingham hydraulics, ECD, stuck pipe physics
│   ├── api-reference.md           # REST & WebSocket endpoint contracts
│   └── demo-script.md             # End-to-end demonstration guide with simulated kicks & pack-offs
│
├── architecture/                  # Visual blueprints and generated system diagrams
│   ├── technical-approach.png
│   ├── system-architecture.png
│   ├── data-flow.png
│   ├── air-gapped-deployment.png
│   └── database-schema.png
│
├── apps/
│   ├── dashboard/                 # Next.js / React 3D Drilling Operations HUD
│   │   ├── app/                   # App router pages & layouts
│   │   ├── components/            # Modular UI components
│   │   │   ├── 3d-well-viewer/    # Three.js 3D trajectory & lithology horizons
│   │   │   ├── live-drilling/     # High-frequency telemetry strip-charts & gauges
│   │   │   ├── alerts/            # Real-time hazard notifications & countdowns
│   │   │   ├── historical-evidence/ # Grounded offset well citations & text excerpts
│   │   │   └── ai-assistant/      # RAG-powered natural language drilling copilot
│   │   ├── lib/                   # WebSocket client, API helpers, coordinate converters
│   │   ├── public/                # Static assets, logos, textures
│   │   ├── package.json           # Frontend dependencies
│   │   └── README.md
│   │
│   └── api/                       # High-performance FastAPI backend gateway
│       ├── app/
│       │   ├── routes/            # Endpoints: telemetry, trajectories, risks, RAG, alerts
│       │   ├── schemas/           # Pydantic v2 schemas and validation models
│       │   ├── services/          # Adapters to core domain microservices
│       │   └── middleware/        # CORS, RBAC, JWT, and telemetry rate-limiting
│       ├── tests/                 # Backend API test suite
│       ├── requirements.txt       # Python dependencies
│       └── README.md
│
├── services/                      # Decoupled core domain services
│   ├── document-intelligence/     # WCR & mudlog parsing, OCR, entity & table extraction
│   ├── telemetry-ingestion/       # WITSML 1.4/2.0 stream parser & Kafka producers/consumers
│   ├── well-geometry/             # Minimum Curvature Method (MCM), 3D spatial linestrings
│   ├── formation-correlation/     # Dynamic Time Warping (DTW) & GR/Resistivity alignment
│   ├── risk-engine/               # XGBoost classifiers & LSTM Autoencoder anomaly detection
│   ├── physics-validation/        # Bingham hydraulics, dynamic ECD, soft-string torque & drag
│   ├── rag-engine/                # Depth-aware chunking, Qdrant retrieval & grounded copilot
│   └── risk-fusion/               # Multi-source Bayesian fusion, severity scoring, SOP builder
│
├── data/
│   ├── synthetic/                 # Realistic Assam-Arakan basin drilling datasets
│   │   ├── wells/                 # Metadata for wells (NHK-421, MOR-118, BGH-07, DGB-02)
│   │   ├── reports/               # WCR excerpts and mud log reports
│   │   ├── telemetry/             # High-frequency CSV drilling telemetry with anomalies
│   │   ├── surveys/               # Directional surveys (MD, Inclination, Azimuth)
│   │   └── well_logs/             # Wireline and LWD LAS logs (GR, RES, RHOB, NPHI)
│   ├── schemas/                   # Strict JSON schemas for validation
│   └── README.md
│
├── database/                      # Persistent storage layers
│   ├── migrations/                # Database versioning migrations
│   ├── seed/                      # Initial seed SQL records
│   ├── postgres/                  # Core relational configs
│   ├── timescaledb/               # High-volume telemetry hypertables & retention policies
│   ├── postgis/                   # 3D spatial coordinates & proximity indexes
│   ├── qdrant/                    # Vector collection config (768-dim embeddings)
│   └── schema.sql                 # Complete unified schema DDL
│
├── models/                        # ML Model artifacts and training pipelines
│   ├── xgboost/                   # Stuck pipe & kick gradient booster
│   ├── lstm/                      # Multivariate temporal autoencoder
│   └── README.md
│
├── infrastructure/                # Orchestration and deployment configs
│   ├── docker/                    # Dockerfiles for API, Frontend, and Workers
│   ├── kafka/                     # Topic definitions & retention configs
│   ├── postgres/                  # DB configuration and extensions
│   ├── qdrant/                    # Qdrant configuration
│   ├── edge-node/                 # Air-gapped rig-site edge node daemon & offline cache
│   └── README.md
│
├── monitoring/                    # Observability & governance
│   ├── health_checks/             # Readiness and liveness probes
│   ├── metrics/                   # Prometheus drilling & inference metrics
│   ├── logging/                   # Structured JSON logging
│   └── audit/                     # Immutable decision audit log
│
├── security/                      # Enterprise defense & data governance
│   ├── rbac/                      # Role-Based Access Control (Driller, Toolpusher, Geologist)
│   ├── audit/                     # Cryptographic audit trail
│   ├── model-integrity/           # SHA256 model weight validation
│   ├── data-governance/           # Field anonymization & export restrictions
│   └── threat-model.md            # Threat matrix & mitigation strategy
│
├── demo/                          # Turnkey interactive demonstration
│   ├── sample_wcr.pdf             # Realistically styled synthetic legacy completion report
│   ├── synthetic_telemetry.csv    # Streaming replay dataset containing a pack-off incident
│   ├── synthetic_surveys.csv      # 3D directional survey stations
│   ├── run_demo.sh                # Automated live scenario execution script
│   └── README.md
│
├── tests/                         # Comprehensive automated test suites
│   ├── integration/               # Multi-service pipeline tests
│   ├── end_to_end/                # Simulated well drilling hazard scenarios
│   ├── performance/               # Telemetry ingestion latency & throughput benchmarks
│   └── test_data/                 # Fixtures and mock data
│
└── scripts/                       # DevOps and operational utilities
    ├── bootstrap.sh               # Environment setup & dependency installation
    ├── seed_database.py           # Loads synthetic Assam Basin wells, logs, and vectors
    ├── start_local_stack.sh       # Launches full local stack
    ├── simulate_telemetry.py      # Real-time telemetry generator with configurable anomalies
    └── run_historical_replay.py   # Replays historical well logs through the risk engine
```

---

## ⚡ Quickstart Guide

### Prerequisites
- **Python 3.10+** (Python 3.12 verified)
- **Node.js 18+** & **npm 9+**
- **Docker & Docker Compose** (Optional for containerized run)

### Option 1: One-Line Local Standalone Execution (No Docker Required)

You can launch StrataSentry directly on your local workstation using the included self-contained SQLite / Mock vector modes:

```bash
# 1. Clone repository and navigate to root
cd STRATASENTRY-NWIS

# 2. Set up virtual environment and install dependencies
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r apps/api/requirements.txt

# 3. Seed synthetic Assam Basin wells, directional surveys, and knowledge base
python scripts/seed_database.py

# 4. Start the FastAPI backend server (Runs on port 8000)
uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload
```

In a second terminal, launch the live drilling telemetry simulator:
```bash
# Streams real-time drilling packet with induced hole pack-off hazard at 2,845m MD
python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff
```

In a third terminal, start the Next.js Tactical HUD:
```bash
cd apps/dashboard
npm install
npm run dev
# Open http://localhost:3000 in your browser
```

---

### Option 2: Full Enterprise Containerized Stack

```bash
# Launch TimescaleDB, PostGIS, Qdrant, Kafka, FastAPI, and Dashboard
docker-compose up -d

# Verify services
docker-compose ps
```

Access Points:
- **Operations Dashboard**: `http://localhost:3000`
- **FastAPI OpenAPI Documentation**: `http://localhost:8000/docs`
- **Qdrant Vector Console**: `http://localhost:6333/dashboard`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

---

## 🛢️ Assam Basin Geological Context (Synthetic Dataset)

The provided synthetic datasets model the litho-stratigraphic succession of the **Upper Assam Shelf** (Moran, Naharkatiya, Digboi, Baghjan areas):

| Depth Range (m TVD) | Stratigraphic Formation | Primary Lithology | Common Drilling Hazards |
|---|---|---|---|
| 0 – 650 m | **Dihing Formation** | Coarse sands, pebble gravels, loose silts | Severe washouts, high torque, shallow water flows |
| 650 – 1,800 m | **Dhekiajuli / Tipam Sandstone** | Thick fluvial quartz sands, intercalated clays | Differential sticking, lost circulation, mud cake buildup |
| 1,800 – 2,550 m | **Girujan Clay** | Massive plastic swelling clays & shales | Clay swelling, tight hole on trips, bit balling |
| 2,550 – 3,400 m | **Barail Formation** | Alternating sandstones, carbonaceous shales, coals | Mechanical hole pack-off, coal seam caving, high gas kicks |
| 3,400 – 3,950 m | **Kopili Formation** | Splintery brittle calcareous shales | Severe wellbore instability, sloughing, stuck pipe |
| 3,950 – 4,400 m | **Sylhet Limestone** | Massive fractured nummulitic limestone | Sudden total lost circulation, cavernous vugs, H2S pockets |

---

## 🔬 Scientific & Engineering Formulas Implemented

- **Minimum Curvature Method (MCM)**:
  $$\beta = \arccos(\cos I_1 \cos I_2 + \sin I_1 \sin I_2 \cos(A_2 - A_1))$$
  $$F = \frac{2}{\beta} \tan\left(\frac{\beta}{2}\right)$$
  $$\Delta TVD = \frac{\Delta MD}{2} (\cos I_1 + \cos I_2) F$$

- **Dynamic Equivalent Circulating Density (ECD)**:
  $$ECD = \rho_{mud} + \frac{\Delta P_{annular}}{0.052 \cdot TVD} + \frac{(1 - \phi_{cuttings})\rho_{rock} \cdot C_{vol}}{0.052 \cdot TVD}$$

- **Mechanical Specific Energy (Teale MSE)**:
  $$MSE = \frac{WOB}{A_b} + \frac{120 \pi \cdot RPM \cdot Torque}{A_b \cdot ROP}$$

- **Corrected d-Exponent (Pore Pressure & Overpressure Detection)**:
  $$d_{exp} = \frac{\log_{10}(ROP / (60 \cdot RPM))}{\log_{10}(12 \cdot WOB / (10^6 \cdot D_{bit}))} \cdot \left(\frac{\rho_{normal}}{\rho_{actual}}\right)$$

---

## 🛡️ Rigorous Testing & Quality Assurance

Run the test suite across all services:
```bash
# Run unit & integration tests
pytest services/ tests/ apps/api/tests/ -v

# Run physics validation benchmark
pytest services/physics-validation/tests/ -v

# Run performance benchmark (simulating 10,000 telemetry packets/sec)
python tests/performance/test_latency_benchmarks.py
```

---

## 📜 Intellectual Property & Citation
Developed under the **Apache 2.0 License**. For academic and industrial citations:
```bibtex
@techreport{stratasentry_nwis_2026,
  title       = {StrataSentry-NWIS: Multi-Modal Physics-Constrained Machine Learning and Depth-Aware RAG for Upstream Drilling Hazard Mitigation},
  institution = {National Well Intelligence Consortium},
  year        = {2026}
}
```
