# Industrial Data Flow & Pipeline Architecture
## StrataSentry-NWIS Data Pipelines

---

## 1. High-Frequency Telemetry Ingestion Pipeline

```
[ Rig Instrumentation: MWD/LWD/Surface Sensors ]
                      |
                      v (WITSML 1.4.1.1 XML / ETP WebSocket)
      [ Telemetry Ingestion Gateway: port 9001 ]
                      |
                      v (Validation & Unit Conversion)
              [ Kafka Producer ]
                      |
       +--------------+--------------+
       | Topic: rig.telemetry.raw    | (10 Hz Partitioned)
       +--------------+--------------+
                      |
                      v
             [ Stream Processor ]
        (Rolling 60-second window buffer)
                      |
       +--------------+--------------+
       |                             |
       v                             v
[ Physics Engine ]             [ ML Risk Engine ]
- Bingham hydraulics          - XGBoost Classifier
- Dynamic ECD                  - LSTM Autoencoder
- Torque & Drag                - Rolling MSE / d_exp
       |                             |
       +--------------+--------------+
                      |
                      v
          [ Risk Fusion Engine ]
     (Severity, Confidence, SOPs)
                      |
       +--------------+--------------+
       |                             |
       v                             v
[ TimescaleDB Hypertable ]    [ WebSocket Broadcaster ]
       |                             |
       v                             v
[ Historical Storage ]        [ Driller Cabin Tactical HUD ]
```

---

## 2. Legacy Document Extraction & RAG Ingestion Pipeline

```
[ Legacy Scanned Well Completion Reports (PDF / TIFF) ]
                      |
                      v
         [ Document Intelligence Service ]
                      |
       +--------------+--------------+
       |                             |
       v                             v
[ PDF Layout Engine ]          [ Tesseract / OCR Engine ]
(Vector text & tables)        (Scanned typed text & stamps)
       |                             |
       +--------------+--------------+
                      |
                      v
          [ Named Entity Recognizer (NER) ]
  - Measured Depths (MD) & True Vertical Depths (TVD)
  - Stratigraphic Tops (e.g., Tipam, Barail, Kopili)
  - Drilling Events (Lost circulation, kicks, stuck pipe)
  - Mitigations (Jarring, pills, sidetracks)
                      |
                      v
       [ Unit Normalizer & Well Name Canonicalizer ]
 (psi -> bar, ppg -> sg, ft -> m, "NHK-421" canonicalized)
                      |
                      v
       [ Depth-Aware Semantic Chunker ]
 (Splits by geological lithology and 20m depth intervals)
                      |
                      v
        [ Domain Embedding Generator ]
       (768-dimensional dense vectors)
                      |
                      v
         [ Qdrant Vector Collection ]
(Payload index: formation, depth_range, incident_type, well_id)
```

---

## 3. Real-Time Decision & Advisory Loop

When an anomalous telemetry pattern is detected:
1. **Sensor Divergence**: Standpipe pressure rises by $180\text{ psi}$ over 40 seconds while ROP decreases from $14\text{ m/hr}$ to $4\text{ m/hr}$ and rotary torque variance triples.
2. **Physics Check**: Dynamic ECD calculates annular friction spike indicating cuttings accumulation in the annulus ($C_v > 0.08$). Bingham model confirms laminar flow regime breakdown.
3. **ML Prediction**: XGBoost evaluates pack-off probability at $0.84$. LSTM autoencoder reconstruction loss crosses the $99^{\text{th}}$ percentile anomaly threshold.
4. **Offset Evidence Retrieval**: RAG queries Qdrant with `current_depth = 2845m`, `formation = 'Barail'`, `hazard = 'packoff'`. Retrieves 3 matching historical incidents in wells *NHK-412* and *MOR-118* with identical coal caving signatures.
5. **Fused Alert Generation**: Severity marked as `WARNING` (escalating to `CRITICAL` in 12 minutes). Standardized driller recommendation issued:
   > *"Stop drilling ahead. Pick up off bottom to 2,830m. Circulate at 2,400 LPM with rotary at 40 RPM to clean hole. Monitor shaker for tabular coal cavings."*
6. **Sub-second Delivery**: Pushed via WebSocket to Driller HUD with acoustic warning tone and visual pulse.
