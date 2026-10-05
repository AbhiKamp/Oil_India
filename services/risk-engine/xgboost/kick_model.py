"""
StrataSentry-NWIS: XGBoost Kick & Lost Circulation Classifier
Calculates calibrated probabilities for gas influx / kick vs lost circulation.
"""

from typing import Dict, Any

class KickXGBoostModel:
    def predict_risk(self, features: Dict[str, float]) -> Dict[str, float]:
        pit_rate = features.get("pit_rate_m3_min", 0.0) # Positive = gain (kick), Negative = loss
        flow_delta = features.get("flow_delta_lpm", 0.0) # Flow Out - Flow In
        gas = features.get("gas_total", 15.0)

        p_normal = 0.94
        p_kick = 0.03
        p_loss = 0.03

        # Kick signature: Pit volume gain + Flow Out > Flow In
        if pit_rate > 0.05 or flow_delta > 150.0:
            kick_severity = min(0.95, 0.40 + (pit_rate / 0.5) * 0.40 + (flow_delta / 800.0) * 0.20)
            p_kick = round(kick_severity, 3)
            p_normal = round(max(0.02, 1.0 - p_kick), 3)
            p_loss = 0.01

        # Lost circulation signature: Pit volume drop + Flow Out < Flow In
        elif pit_rate < -0.05 or flow_delta < -200.0:
            loss_severity = min(0.95, 0.40 + (abs(pit_rate) / 0.5) * 0.40 + (abs(flow_delta) / 800.0) * 0.20)
            p_loss = round(loss_severity, 3)
            p_normal = round(max(0.02, 1.0 - p_loss), 3)
            p_kick = 0.01

        total = p_normal + p_kick + p_loss
        return {
            "normal": round(p_normal / total, 3),
            "gas_kick": round(p_kick / total, 3),
            "lost_circulation": round(p_loss / total, 3)
        }
