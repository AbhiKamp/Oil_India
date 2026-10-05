# StrataSentry-NWIS Technical Architecture
## Detailed Microservice Specifications, Protocols, and Latency Budgets

---

## 1. System Communication Protocols & Data Contracts

```
[ Rig Floor Sensors ] ---> [ WITSML 1.4.1.1 / WITSML 2.0 (ETP/WebSocket) ]
                                   |
                                   v
[ Kafka Ingestion ] ------> [ Topic: rig.telemetry.raw (Avro/JSON) ]
                                   |
                                   v
[ Analytics Core ] -------> [ In-Memory Ring Buffer (NumPy / SciPy) ]
                                   |
                                   v
[ Fusion Engine ] --------> [ Topic: rig.alerts.immediate (JSON) ]
                                   |
                                   v
[ FastAPI Gateway ] ------> [ WebSocket: /ws/telemetry (Binary/JSON) ]
                                   |
                                   v
[ Driller HUD ] ----------> [ React / Three.js 60 FPS Render Loop ]
```

### 1.1 Ingestion Latency Budget (Target: < 500 ms)

| Processing Stage | Implementation | Max Allowed Latency | Typical Measured Latency |
|---|---|---|---|
| **Sensor Acquisition to Rig Edge Gateway** | WITSML / MWD telemetry modem | 150 ms | 60 ms |
| **Kafka Ingest & Stream Normalization** | Python fast-avro / schema validator | 50 ms | 18 ms |
| **Minimum Curvature 3D Trajectory Update** | Cython / NumPy vector operations | 20 ms | 4 ms |
| **Physics Hydraulics & ECD Validation** | Analytical Bingham Plastic solver | 40 ms | 12 ms |
| **ML Inference (XGBoost + LSTM Autoencoder)** | ONNX Runtime / PyTorch C++ CPU | 60 ms | 28 ms |
| **Dynamic Time Warping Formation Alignment** | Constrained Sakoe-Chiba DTW | 50 ms | 22 ms |
| **Risk Fusion & Alert Assembly** | In-memory Bayesian matrix | 30 ms | 8 ms |
| **WebSocket Broadcast to Driller Display** | Starlette async WebSocket broadcaster | 50 ms | 15 ms |
| **Total End-to-End Processing Budget** | **Ingestion to Visual Driller Alert** | **< 500 ms** | **~167 ms** |

---

## 2. Microservice Topology

### 2.1 FastAPI Gateway (`apps/api`)
- High-performance asynchronous REST and WebSocket API built on Starlette and Pydantic v2.
- Handles telemetry streaming, alert broadcasts, document ingestion pipelines, and interactive RAG queries.
- Incorporates rate-limiting and connection pooling for multi-rig fleet monitoring.

### 2.2 Telemetry Ingestion Microservice (`services/telemetry-ingestion`)
- Contains a standalone WITSML SOAP and ETP client for standard rig data loggers (NOV, Halliburton Insite, Schlumberger InterOp).
- Standardizes diverse oilfield engineering units (e.g., metric bar/m/lpm to oilfield psi/ft/gpm and vice versa) using `services/document-intelligence/normalizers/units.py`.

### 2.3 Well Geometry Engine (`services/well-geometry`)
- Takes raw directional survey stations $(MD, Inc, Azi)$ and applies the mathematical Minimum Curvature algorithm.
- Computes $TVD$, $\Delta Northing$, $\Delta Easting$, Dogleg Severity ($DLS$), and vertical section.
- Translates coordinates into EPSG:32646 (UTM Zone 46N, covering Upper Assam) for PostGIS spatial integration.

### 2.4 Physics Validation Engine (`services/physics-validation`)
- Runs closed-form non-Newtonian annular pressure loss calculations:
  - Bingham Plastic model ($PV, YP$)
  - Power Law & Herschel-Bulkley models
  - Dynamic ECD accounting for cuttings loading concentration
  - Soft-string Torque & Drag friction factor regression
  - Kick mass balance (Flow-in vs Flow-out, pit gain integration)

### 2.5 Risk Engine & ML Inferencing (`services/risk-engine`)
- Feature engineering extracts 18 rolling statistical derivatives:
  - Mechanical Specific Energy ($\text{MSE}$)
  - Corrected $d$-exponent ($d_{exp}$)
  - Annular pack-off index ($API = \frac{d(SPP)}{dt} \cdot \frac{1}{\text{ROP}}$)
  - Differential sticking susceptibility index ($DSSI = (ECD - P_{pore}) \cdot \Delta t_{stationary}$)
- Machine Learning models:
  - LightGBM / XGBoost classifier calibrated with isotonic regression.
  - PyTorch LSTM autoencoder calculating reconstruction error across 12 normalized telemetry channels.

### 2.6 Depth-Aware RAG Engine (`services/rag-engine`)
- Integrates with Qdrant vector database using dense embeddings (768 dimensions).
- Uses hybrid metadata filtering: searches are scoped by stratigraphic formation (e.g., `formation == 'Barail'`), depth proximity ($\pm 100\text{ m}$), and hazard category (`stuck_pipe`, `gas_kick`, `lost_circulation`).
- Formats grounded prompt templates for local LLM inference (Mistral-7B Instruct or Ollama).

---

## 3. Persistent Storage Schemas

1. **TimescaleDB**:
   - Continuous 10 Hz / 1 Hz drilling telemetry stored in hypertables partitioned by time chunks.
   - Downsampled retention policies (10 Hz raw kept for 14 days, 1 Hz kept for lifetime of well, 10-second averages kept permanently).
2. **PostgreSQL + PostGIS**:
   - Relational entities: `wells`, `wellbores`, `directional_surveys`, `formation_tops`, `casing_strings`, `incidents`.
   - 3D Linestring geometries (`LINESTRING Z`) representing actual well trajectories and planned trajectories.
3. **Qdrant Vector Database**:
   - Unstructured knowledge chunks extracted from legacy Well Completion Reports (WCR), daily drilling reports (DDR), and mud logs.
   - Exact metadata payloads: `well_name`, `wcr_id`, `md_top`, `md_bottom`, `formation`, `lithology`, `incident_type`, `mitigation_summary`.
