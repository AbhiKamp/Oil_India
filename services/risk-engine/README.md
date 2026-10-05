# Risk Engine

Real-time drilling hazard prediction combining physical feature engineering, calibrated XGBoost classifiers, and multivariate LSTM Autoencoders.

---

## Architecture

- **`feature_engineering/`**: Computes rolling Teale Mechanical Specific Energy ($\text{MSE}$), Jordan $d$-exponent, $\frac{d(SPP)}{dt}$ pressure slope, and torque volatility.
- **`xgboost/`**:
  - `stuck_pipe_model.py`: Probabilities for mechanical hole pack-off and differential sticking.
  - `kick_model.py`: Mass balance probability for gas kicks and lost circulation.
- **`lstm_autoencoder/`**:
  - `detector.py`: Unsupervised temporal anomaly detection on 12 simultaneous sensor streams.
- **`thresholds/`**:
  - `dynamic_thresholds.py`: Formation-adaptive alarm envelopes.
- **`inference/`**:
  - `predictor.py`: Orchestrates end-to-end evaluation pipeline.
