# Document Intelligence Service

The **Document Intelligence Service** converts unstructured legacy Well Completion Reports (WCR), daily drilling reports (DDR), and wireline logs into structured geological and operational incident records.

---

## Capabilities

- **`parsers/`**:
  - `pdf_parser.py`: Extracts vector text and structured sections from PDF and ASCII WCR documents.
  - `ocr_parser.py`: Prepares and extracts scanned microfiche text.
  - `table_parser.py`: Regex and tabular parser for casing setting depths and mud programs.
- **`extractors/`**:
  - `depth_extractor.py`: Identifies MD and TVD measurements and depth intervals.
  - `formation_extractor.py`: Matches Assam Basin stratigraphy (Tipam, Girujan, Barail, Kopili, Sylhet).
  - `event_extractor.py`: Categorizes drilling hazards (mechanical pack-off, differential sticking, kicks, losses).
  - `mitigation_extractor.py`: Extracts fishing steps, jarring overpull, and mud kill operations.
- **`normalizers/`**:
  - `units.py`: Converts between oilfield, metric, and SI units (psi, bar, ppg, SG, gpm, LPM).
  - `well_names.py`: Resolves legacy well naming variants into canonical formats.
- **`confidence/`**:
  - `confidence_evaluator.py`: Quantifies entity extraction confidence ($0.0 - 1.0$).
