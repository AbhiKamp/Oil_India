# Risk Fusion Engine

Heuristic risk arbitration combining telemetry rules and optional offset evidence. Scores are uncalibrated and are not field-validated.

---

## Capabilities

- **`fusion_engine.py`**:
  - Coordinates multi-signal arbitration.
- **`severity.py`**:
  - Computes heuristic severity (`INFO`, `WATCH`, `WARNING`, `CRITICAL`); incident countdown is not estimated.
- **`confidence.py`**:
  - Unified multi-modal confidence scoring.
- **`alert_builder.py`**:
  - Standardized JSON alert packaging.
- **`recommendation_builder.py`**:
  - Step-by-step driller Standard Operating Procedures (SOPs).
