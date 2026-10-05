# Depth-Aware RAG Methodology & Citation Grounding
## Retrieval-Augmented Generation for Oilfield Drilling Operations

---

## 1. Why Standard RAG Fails in Petroleum Engineering

Standard document retrieval systems break down when applied to drilling completion reports for three key reasons:
1. **Disregard for Physical Depth**: Chunking by fixed token lengths (e.g., 512 tokens) fractures critical depth correlations. An event occurring at $2,845\text{ m}$ MD might get severed from its corresponding mud weight ($1.38\text{ SG}$) or BHA stabilizer configuration listed 15 lines earlier.
2. **Stratigraphic Amnesia**: Geologically, an incident at $2,800\text{ m}$ in a *Tipam* sandstone cannot be directly compared to $2,800\text{ m}$ in an overpressured *Barail* coal seam. Retrieval must be stratigraphically constrained.
3. **Hallucination of Safety-Critical Metrics**: In an operational driller cabin, recommending the wrong kill mud weight or incorrect pump rate can cause catastrophic blowout or hydraulic fracturing of the casing shoe.

---

## 2. Depth-Aware Semantic Chunking Strategy

StrataSentry implements **Stratigraphically-Aware, Depth-Indexed Chunking**:

```
+---------------------------------------------------------------------------------+
|                       RAW WELL COMPLETION REPORT (WCR)                          |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
| SECTION BOUNDARY DETECTION                                                      |
| Detects: Casing Program, Mud Program, Geological Tops, Drilling Incidents       |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
| DEPTH INTERVAL ANCHORING                                                        |
| Every chunk is assigned an explicit physical bounding box:                     |
| {                                                                               |
|   "well_name": "MOR-118",                                                       |
|   "formation": "Barail Coal-Shale",                                             |
|   "depth_interval_md": [2830.0, 2865.0],                                        |
|   "tvd_interval": [2710.0, 2742.0],                                             |
|   "lithology": "Carbonaceous splintery shale intercalated with coal",          |
|   "hazard_type": "Mechanical Pack-off & Stuck Pipe",                            |
|   "incident_flag": true                                                         |
| }                                                                               |
+---------------------------------------------------------------------------------+
```

---

## 3. Vector Storage & Hybrid Retrieval in Qdrant

Chunks are embedded into 768-dimensional dense vector spaces using domain-adapted transformer models.

### Retrieval Filter Query:
```json
{
  "filter": {
    "must": [
      { "key": "formation", "match": { "value": "Barail Coal-Shale" } },
      { "key": "incident_type", "match": { "value": "hole_packoff" } }
    ],
    "should": [
      {
        "key": "md_top",
        "range": {
          "gte": 2750.0,
          "lte": 2950.0
        }
      }
    ]
  }
}
```
This guarantees that when the active well enters the *Barail* formation at $2,845\text{ m}$, the system retrieves only contextually relevant offset well precedents within that exact geological facies.

---

## 4. Citation Grounding & Zero-Hallucination Guardrails

Before the LLM response is displayed to the driller or toolpusher, the **Citation Grounding Engine** (`services/rag-engine/citations/citation_grounding.py`) applies verification checks:
1. **Verification of Document Existence**: Every cited Well Name (e.g., `NHK-412`) must exist in the database index.
2. **Numerical Sanity Check**: Mud weights cited in recommendations must not exceed the casing burst rating or formation fracture gradient stored in the well schema.
3. **Structured Attribution Format**:
   - `[Ref: Well MOR-118 | Depth: 2,848m MD | Barail Formation | WCR Sec 4.1]`
