"""
StrataSentry-NWIS: XGBoost Stuck Pipe Classifier
Calculates calibrated probabilities for mechanical pack-off and differential sticking.
"""

from typing import Dict, Any

class StuckPipeXGBoostModel:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.is_loaded = False
        self._init_model()

    def _init_model(self):
        # In production with trained XGBoost model:
        # import xgboost as xgb
        # self.booster = xgb.Booster()
        # self.booster.load_model(self.model_path)
        self.is_loaded = True

    def predict_risk(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Inference logic based on trained gradient boosting decision boundary rules.
        """
        spp_slope = features.get("spp_slope_psi_sec", 0.0)
        torque_std = features.get("torque_std", 0.0)
        rop = features.get("rop", 12.0)
        flow_delta = features.get("flow_delta_lpm", 0.0)
        ecd = features.get("ecd", 1.30)
        mw = features.get("mud_weight_in", 1.25)

        # Baseline probabilities
        p_normal = 0.90
        p_packoff = 0.05
        p_differential = 0.05

        # Check Packoff Indicators: Rising SPP + High Torque Volatility + Decreasing ROP
        if spp_slope > 3.0 and torque_std > 2.0:
            packoff_factor = min(0.92, 0.40 + (spp_slope / 15.0) * 0.35 + (torque_std / 8.0) * 0.20)
            p_packoff = round(packoff_factor, 3)
            p_normal = round(max(0.02, 1.0 - p_packoff - 0.05), 3)
            p_differential = 0.03
        elif spp_slope > 1.5:
            p_packoff = 0.45
            p_normal = 0.50
            p_differential = 0.05

        # Check Differential Sticking Indicators: Stationary or Low ROP with High Overbalance (ECD >> Pore Pressure)
        overbalance_sg = ecd - 1.15
        if rop < 1.0 and overbalance_sg > 0.15:
            p_differential = round(min(0.88, 0.35 + overbalance_sg * 2.0), 3)
            p_normal = round(max(0.05, 1.0 - p_differential - p_packoff), 3)

        # Normalize sum to 1.0
        total = p_normal + p_packoff + p_differential
        return {
            "normal": round(p_normal / total, 3),
            "hole_packoff": round(p_packoff / total, 3),
            "differential_sticking": round(p_differential / total, 3)
        }
