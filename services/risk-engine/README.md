# Risk Engine

Read-only drilling signal assessment using physical feature engineering and explicitly uncalibrated heuristic baselines. No trained XGBoost or LSTM artifact is loaded; the NumPy projection is an untrained stand-in, not an evaluated anomaly model. No source training dataset or field evaluation is available.

---

## Architecture

- **`feature_engineering/`**: Computes rolling Teale Mechanical Specific Energy ($\text{MSE}$), Jordan $d$-exponent, $\frac{d(SPP)}{dt}$ pressure slope, and torque volatility.
- **`xgboost/`**: Handwritten heuristic scores only; despite filenames, these modules do not load XGBoost artifacts and outputs are not calibrated probabilities.
- **`lstm_autoencoder/`**:
  - `detector.py`: Untrained NumPy projection score; not a trained LSTM or validated anomaly detector.
- **`thresholds/`**:
  - `dynamic_thresholds.py`: Formation-adaptive alarm envelopes.
- **`inference/`**:
  - `predictor.py`: Orchestrates end-to-end evaluation pipeline.
