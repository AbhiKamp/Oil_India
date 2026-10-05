"""
StrataSentry-NWIS: LSTM Temporal Anomaly Detector
Tracks multivariate reconstruction error and triggers statistical anomaly scores.
"""

import numpy as np
from typing import List, Dict, Any
from .model import LSTMAutoencoderArchitecture

class LSTMAnomalyDetector:
    def __init__(self, threshold: float = 0.45):
        self.model = LSTMAutoencoderArchitecture()
        self.threshold = threshold

    def detect_anomaly(self, feature_matrix: np.ndarray) -> Dict[str, Any]:
        """
        feature_matrix shape: (seq_len, n_features)
        Returns reconstruction loss and anomaly status.
        """
        if feature_matrix.ndim == 2:
            x = np.expand_dims(feature_matrix, axis=0)
        else:
            x = feature_matrix

        x_recon = self.model.forward(x)
        # Mean Squared Error reconstruction loss
        loss = float(np.mean((x - x_recon) ** 2))

        is_anomalous = loss > self.threshold
        anomaly_confidence = round(min(1.0, loss / (self.threshold * 2.0)), 3)

        return {
            "reconstruction_loss": round(loss, 4),
            "anomaly_threshold": self.threshold,
            "is_anomaly": is_anomalous,
            "anomaly_confidence": anomaly_confidence
        }
