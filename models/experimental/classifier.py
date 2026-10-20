"""NumPy-only softmax classifier; classifies the current synthetic window."""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

LABELS = ("normal", "packoff", "kick")
FEATURE_NAMES = ("spp_mean", "spp_slope_per_second", "rop_mean", "torque_mean", "pit_gain", "flow_out_pct_mean")
ARTIFACT = Path(__file__).with_name("artifacts") / "synthetic_softmax.json"


def _timestamp(value):
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def extract_features(window):
    """Return ordered causal features from frames containing timestamp and telemetry fields."""
    if not isinstance(window, (list, tuple)) or len(window) < 2:
        raise ValueError("window must contain at least two telemetry frames")
    try:
        times = np.array([_timestamp(row["timestamp"]).timestamp() for row in window])
        values = {key: np.array([float(row[key]) for row in window]) for key in ("standpipe_pressure", "rop", "surface_torque", "pit_volume", "flow_out_pct")}
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("frames require valid timestamp, SPP, ROP, torque, and pit_volume") from exc
    if not all(np.all(np.isfinite(v)) for v in [times, *values.values()]) or np.any(np.diff(times) <= 0):
        raise ValueError("telemetry values must be finite and timestamps strictly increasing")
    elapsed = times - times[0]
    pit_slope = float(np.polyfit(elapsed, values["pit_volume"], 1)[0])
    spp_slope = float(np.polyfit(elapsed, values["standpipe_pressure"], 1)[0])
    return np.array([values["standpipe_pressure"].mean(), spp_slope, values["rop"].mean(), values["surface_torque"].mean(), pit_slope, values["flow_out_pct"].mean()], dtype=float)


def load_model(path=ARTIFACT):
    """Load and validate a JSON artifact; missing weights are never silently substituted."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError("experimental model artifact missing: {} (run python -m models.experimental.train)".format(path))
    artifact = json.loads(path.read_text())
    if artifact.get("feature_names") != list(FEATURE_NAMES) or artifact.get("labels") != list(LABELS):
        raise ValueError("model artifact feature order or labels are incompatible")
    try:
        mean = np.asarray(artifact["mean"], dtype=float)
        scale = np.asarray(artifact["scale"], dtype=float)
        weights = np.asarray(artifact["weights"], dtype=float)
        bias = np.asarray(artifact["bias"], dtype=float)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("model artifact is missing valid numeric parameters") from exc
    if mean.shape != (len(FEATURE_NAMES),) or scale.shape != mean.shape or weights.shape != (len(FEATURE_NAMES), len(LABELS)) or bias.shape != (len(LABELS),):
        raise ValueError("model artifact parameter shapes are incompatible")
    if not all(np.all(np.isfinite(value)) for value in (mean, scale, weights, bias)) or np.any(scale <= 0):
        raise ValueError("model artifact parameters must be finite and scales positive")
    return artifact


def predict(window, model=None):
    model = model or load_model()
    x = (extract_features(window) - np.asarray(model["mean"])) / np.asarray(model["scale"])
    logits = x @ np.asarray(model["weights"]) + np.asarray(model["bias"])
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()
    index = int(probs.argmax())
    return {"label": LABELS[index], "scores": dict(zip(LABELS, map(float, probs))), "scope": "current synthetic pattern classification; not future incident prediction"}
