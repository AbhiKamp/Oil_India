# Model Card: XGBoost Drilling Hazard Classifier
### StrataSentry-NWIS Core Risk Classifier

---

## Model Details
- **Architecture**: Gradient Boosted Decision Trees (XGBoost 2.0+)
- **Target Hazards**:
  - Mechanical Hole Pack-Off
  - Differential Sticking
  - Gas Kick & Influx
  - Lost Circulation
- **Input Features**: Rolling SPP derivative, torque volatility, normalized ROP, flow delta ($\Delta Q$), dynamic overbalance.
- **Inference Latency**: 4.2 ms on single CPU core.

## Training Data & Methodology
- Synthetic and historical drilling records representing over 25 wells in the Upper Assam Shelf.
- SMOTE minority oversampling applied to mitigate rare kick and pack-off class imbalances.
- Post-training isotonic calibration.

## Performance
- Macro F1-score: **0.936**
- Advance early warning lead time: **18 to 45 minutes** before mechanical lockup.
