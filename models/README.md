# Machine Learning Models Directory

This directory contains model definitions, training scripts, evaluation benchmarks, and formal model cards for StrataSentry-NWIS.

---

## Subdirectories

- **`xgboost/`**:
  - `train.py`: Trains multi-class gradient boosted decision trees.
  - `evaluate.py`: Generates precision/recall/F1 metrics.
  - `model_card.md`: Technical documentation and bias assessment.
- **`lstm/`**:
  - `train.py`: Unsupervised multivariate autoencoder training pipeline.
  - `evaluate.py`: ROC-AUC reconstruction error benchmark.
  - `model_card.md`: Architecture specifics and bottleneck dimensions.
