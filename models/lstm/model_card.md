# Model Card: LSTM Temporal Autoencoder
### StrataSentry-NWIS Multivariate Drilling Anomaly Detector

---

## Model Details
- **Architecture**: 2-layer Bidirectional LSTM Encoder + 2-layer LSTM Decoder with 16-dim latent bottleneck.
- **Input Dimensions**: $(B, 60, 12)$ corresponding to 60-second sliding windows across:
  - ROP, WOB, Torque, RPM, Standpipe Pressure, Flow In, Flow Out, Pit Volume, Mud Weight, ECD, Gamma Ray, MSE.
- **Inference Time**: 12.4 ms on CPU.

## Intended Use
- Detects subtle sensor drift, micro-annular obstructions, and unmodeled drillstring dynamics before threshold violations occur.
- Operates in unsupervised mode, making it robust to novel geological formations.
