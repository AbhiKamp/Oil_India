# StrataSentry-NWIS Solution Overview
## Next-Generation National Well Intelligence Platform

---

## 1. System Vision & Architecture Matrix

StrataSentry-NWIS bridges the critical divide between retrospective well engineering archives and real-time downhole sensor streaming.

```
+----------------------------------------------------------------------------------------------------+
|                                    STRATASENTRY-NWIS PLATFORM                                      |
+-----------------------------------+--------------------------------+-------------------------------+
|     LEGACY KNOWLEDGE CORE         |   REAL-TIME STREAMING CORE     |   DRILLER ADVISORY CORE       |
+-----------------------------------+--------------------------------+-------------------------------+
| - Multi-Modal WCR / PDF Parser    | - High-throughput WITSML / MWD | - 3D Three.js Wellbore HUD    |
| - Domain NER & Table Extraction   | - Minimum Curvature Trajectory | - Multi-Hazard Strip Charts   |
| - Lithology & Formation Top Match | - Bingham / ECD Hydraulics     | - Sub-minute Severity Alerts  |
| - Depth-Aware Qdrant Vector Store | - XGBoost & LSTM Autoencoder   | - Grounded Drilling Copilot   |
+-----------------------------------+--------------------------------+-------------------------------+
```

---

## 2. Key Pillars of the Solution

### Pillar 1: Document Intelligence & Legacy Archive Unification
Legacy completion reports, mud logging reports, and geological lithology logs are ingested and processed through specialized domain parsers:
- **Depth-Aware Chunking**: Chunks are bounded by physical measured depth (MD) intervals and stratigraphic tops rather than arbitrary token counts.
- **Entity Extraction**: Automated identification of drill collars, stabilizer placements, mud weights, bit types (PDC, Tricone), loss zones, stuck pipe depths, and fishing operations.
- **Stratigraphic Normalization**: Assam Basin formations are normalized across decades of inconsistent naming (e.g., *Tipam Sand*, *TPS*, *Tipam Sandstone Formation* -> `Tipam Sandstone`).

### Pillar 2: High-Frequency Telemetry Ingestion & Trajectory Computation
- Streams WITSML 1.4.1/2.0 sensor feeds at up to 10 Hz through an Apache Kafka message bus.
- Continuously computes the true 3D borehole spatial position using the **Minimum Curvature Method (MCM)**, outputting True Vertical Depth (TVD), Northing, Easting, and Dogleg Severity (DLS) with collision cone error bounding.

### Pillar 3: Real-Time Formation Correlation (Ahead of Bit)
- Correlates downhole MWD Gamma Ray ($GR$) and deep resistivity ($RES$) logs against offset reference wells using **Dynamic Time Warping (DTW)**.
- Predicts impending formation boundary crossings (e.g., *Barail Coal* top at $2,835\text{ m}$ MD) ahead of the bit, allowing the mud engineer to adjust density before overpressured zones are penetrated.

### Pillar 4: Physics-Constrained Machine Learning Risk Fusion
- **XGBoost Classifier**: Multi-hazard probability calculation trained on multi-sensor feature derivatives ($\frac{d(SPP)}{dt}$, $\Delta \text{Flow}$, $\text{MSE}$, Torque standard deviation).
- **LSTM Autoencoder**: Detects subtle multivariate divergence across 12 simultaneous telemetry channels without requiring labeled anomaly data.
- **Deterministic Physics Gates**: Validates whether observed telemetry satisfies physical laws (differential pressure sticking limits, cuttings slip velocity, Bingham plastic annular friction).
- **Severity Index**: Fuses ML scores, physics violations, and historical offset incidents into an actionable risk classification: `INFO`, `WATCH`, `WARNING`, `CRITICAL`.

### Pillar 5: Depth-Aware RAG Copilot
- Connects drillers and operations geologists directly to legacy well archives via natural language.
- Every response is strictly grounded in retrieved evidence, citing:
  - Reference Well Identifier (e.g., `Well MOR-118`)
  - Precise Depth Interval (e.g., `2,840.5 - 2,852.0 m MD`)
  - Source Document & Page (e.g., `WCR MOR-118, Section 4.2, Page 17`)
  - Primary Mechanism & Recommended Mitigation

### Pillar 6: Operational Driller Cabin HUD
- A dark-mode, high-contrast, industrial touchscreen tactical interface optimized for driller cabin conditions.
- Interactive 3D wellbore trajectory rendered with WebGL / Three.js displaying active drill bit location, offset wellbores, formation horizon surfaces, and colored risk zones.
- Real-time gauge cluster, dynamic scrolling log curves, instant acoustic/visual alerts, and SOP recommendation drawer.
