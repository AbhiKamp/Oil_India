"""
StrataSentry-NWIS: Multi-Model Risk Predictor
Coordinates Feature Engineering, XGBoost Classifiers, and LSTM Autoencoder.
"""

from typing import List, Dict, Any
import numpy as np

try:
    from ..feature_engineering.drilling_features import DrillingFeatureEngineer
    from ..xgboost.stuck_pipe_model import StuckPipeXGBoostModel
    from ..xgboost.kick_model import KickXGBoostModel
    from ..lstm_autoencoder.detector import LSTMAnomalyDetector
    from ..thresholds.dynamic_thresholds import DynamicThresholdManager
except ImportError:
    from feature_engineering.drilling_features import DrillingFeatureEngineer
    from xgboost.stuck_pipe_model import StuckPipeXGBoostModel
    from xgboost.kick_model import KickXGBoostModel
    from lstm_autoencoder.detector import LSTMAnomalyDetector
    from thresholds.dynamic_thresholds import DynamicThresholdManager

class DrillingRiskPredictor:
    def __init__(self):
        self.feat_eng = DrillingFeatureEngineer()
        self.stuck_pipe_model = StuckPipeXGBoostModel()
        self.kick_model = KickXGBoostModel()
        self.lstm_detector = LSTMAnomalyDetector()

    def evaluate_window(self, telemetry_window: List[Dict[str, Any]], formation: str = "Barail Coal-Shale") -> Dict[str, Any]:
        """
        Runs complete inference pipeline over rolling telemetry window.
        """
        if not telemetry_window:
            return {}

        current_depth = telemetry_window[-1].get("measured_depth", 0.0)
        features = self.feat_eng.extract_features(telemetry_window)

        # 1. XGBoost predictions
        stuck_risks = self.stuck_pipe_model.predict_risk(features)
        kick_risks = self.kick_model.predict_risk(features)

        # 2. LSTM multivariate reconstruction anomaly
        # Build 2D feature matrix for recent points
        recent = telemetry_window[-20:]
        matrix = []
        for f in recent:
            row = [
                f.get("rop", 0.0) / 30.0,
                f.get("wob", 0.0) / 25.0,
                f.get("surface_torque", 0.0) / 30.0,
                f.get("rotary_rpm", 0.0) / 150.0,
                f.get("standpipe_pressure", 0.0) / 4000.0,
                f.get("flow_in", 0.0) / 3500.0,
                f.get("flow_out_pct", 0.0) / 100.0,
                f.get("pit_volume", 0.0) / 60.0,
                f.get("ecd", 0.0) / 2.0,
                f.get("gamma_ray", 0.0) / 150.0,
                f.get("gas_total", 0.0) / 100.0,
                features.get("mse_ksi", 0.0) / 200.0
            ]
            matrix.append(row)
        lstm_res = self.lstm_detector.detect_anomaly(np.array(matrix))

        # 3. Dynamic thresholds
        thresholds = DynamicThresholdManager.get_thresholds(formation, current_depth)

        # Consolidate probabilities
        ml_probs = {
            "normal": min(stuck_risks["normal"], kick_risks["normal"]),
            "hole_packoff": stuck_risks["hole_packoff"],
            "differential_sticking": stuck_risks["differential_sticking"],
            "gas_kick": kick_risks["gas_kick"],
            "lost_circulation": kick_risks["lost_circulation"]
        }

        # Normalize
        s = sum(ml_probs.values())
        if s > 0:
            for k in ml_probs:
                ml_probs[k] = round(ml_probs[k] / s, 3)

        return {
            "measured_depth": current_depth,
            "formation": formation,
            "features": features,
            "ml_probabilities": ml_probs,
            "lstm_anomaly": lstm_res,
            "active_thresholds": thresholds
        }
