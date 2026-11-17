# Experimental synthetic telemetry classifier

Train and regenerate both artifacts from the repository root:

```sh
python -m models.experimental.train
python -m pytest tests/test_experimental_model.py -q
```

API usage (frames are chronological mappings with `timestamp`, `standpipe_pressure`, `rop`, `surface_torque`, `pit_volume`, and `flow_out_pct`):

```python
from models.experimental.classifier import predict

result = predict(recent_frames)  # loads artifacts/synthetic_softmax.json
```

`extract_features(recent_frames)` is reusable independently. Features, in artifact order, are mean SPP, timestamp-based SPP slope (pressure units/second), mean ROP, mean surface torque, timestamp-based pit slope, and mean flow-out percentage. The artifact stores these names, normalization, weights, labels, version, generator version/seed, and generator-spec SHA-256.

Artifacts are `artifacts/synthetic_softmax.json` and `artifacts/evaluation.json`. The JSON artifact schema is `softmax-v1`: `feature_names`, `labels`, `mean[N]`, `scale[N]`, `weights[N][3]`, `bias[3]`, `dataset_generator`, `dataset_seed`, `dataset_spec_sha256`. `load_model` validates exact shapes and finite parameters, and requires strictly positive scales.

Current committed artifact SHA-256: `a9ba04fca0f8db343b1cfbb2bb64f8004075db1278c81361bf0e173db6251d1b`. Generator seed is `26121`; the report records the grouped split and its measured results. This one generated holdout measured 0.9815 accuracy versus 0.7778 for the majority baseline (normal 1.00 precision/0.9762 recall; packoff 1.00/1.00; kick 0.8571/1.00). These figures describe this synthetic dataset only.

Ground-truth labels describe the **current synthetic pattern**. Packoff/kick traces are normal through frame 59, frames 60–69 are an omitted ambiguous transition window, and anomalous labels begin at frame 70. Windows are ten consecutive frames; no future frames enter features. Each generated well contains all three scenarios, and all scenarios/windows for a well stay on one side of a deterministic 8/2 well-ID split. Synthetic well IDs are generator grouping keys, not independent real wells.

Limitations: all observations are generated; this does not establish field predictive accuracy, reliability, calibration, incident warning lead time, false alerts per operating hour, or prevented incidents. Test metrics are based on only two synthetic generator well IDs and have limited generalizability; synthetic IDs are not independent observed wells. The measured metrics and confusion matrices belong only to this generated holdout and are not operational performance claims. No field telemetry or OIL data are used. The model classifies present/past windows; it does not predict future incidents.
