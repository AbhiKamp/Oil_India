"""Reproducibly generate, group-split, train, and evaluate synthetic telemetry."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from .classifier import ARTIFACT, FEATURE_NAMES, LABELS, extract_features

SEED = 26121
GENERATOR_VERSION = "synthetic-current-labels-v2"


def generate(seed=SEED):
    rng = np.random.default_rng(seed)
    groups = []
    # Each well has all three scenarios; wells, not traces/windows, define the split.
    for scenario in LABELS:
        for well in range(10):
            group = "well{:02d}".format(well)
            base = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=(well * 3 + LABELS.index(scenario)) * 10000)
            frames = []
            spp0, torque0, rop0, pit0 = rng.normal(2800, 90), rng.normal(15, 1.5), rng.normal(14, 1.3), rng.normal(40, 1)
            flow0 = rng.normal(75, 2)
            elapsed = 0.0
            for t in range(100):
                phase = max(0, t - 60)
                if scenario == "packoff":
                    spp, rop, torque, pit, flow = spp0 + phase * 8, rop0 - phase * .12, torque0 + phase * .12, pit0 - phase * .005, flow0 - phase * .18
                elif scenario == "kick":
                    spp, rop, torque, pit, flow = spp0 + phase * 1.2, rop0 + phase * .01, torque0, pit0 + phase * .035, flow0 + phase * .12
                else:
                    spp, rop, torque, pit, flow = spp0, rop0, torque0, pit0, flow0
                elapsed += rng.uniform(.8, 1.2)
                frames.append({"timestamp": (base + timedelta(seconds=elapsed)).isoformat(),
                               "standpipe_pressure": spp + rng.normal(0, 22), "rop": max(0, rop + rng.normal(0, .65)),
                               "surface_torque": torque + rng.normal(0, .8), "pit_volume": pit + rng.normal(0, .12),
                               "flow_out_pct": flow + rng.normal(0, .5)})
            groups.append((group, scenario, frames))
    return groups


def evaluate(y, pred):
    matrix = [[int(np.sum((y == i) & (pred == j))) for j in range(3)] for i in range(3)]
    per_class = {}
    for i, label in enumerate(LABELS):
        tp = matrix[i][i]
        per_class[label] = {"precision": tp / max(1, sum(row[i] for row in matrix)), "recall": tp / max(1, sum(matrix[i]))}
    return {"accuracy": float(np.mean(y == pred)), "confusion_matrix_true_rows_pred_columns": matrix, "per_class": per_class}


def split_group_indices(count, seed=SEED):
    order = np.random.default_rng(seed + 1).permutation(count)
    test = set(order[::5].tolist())
    return set(range(count)) - test, test


def window_label(scenario, start, width=10):
    """Label only observed phase; drop windows overlapping the uncertain onset transition."""
    if start + width <= 60:
        return "normal"
    if start >= 70:
        return scenario
    return None


def main():
    groups = generate()
    train_well_ids, test_well_ids = split_group_indices(10)
    train_rows, test_rows, train_y, test_y, train_groups, test_groups = [], [], [], [], set(), set()
    train_wells, test_wells = set(), set()
    for index, (group, label, frames) in enumerate(groups):
        well_index = int(group[4:])
        is_test = well_index in test_well_ids
        target_rows, target_y = (test_rows, test_y) if is_test else (train_rows, train_y)
        (test_groups if is_test else train_groups).add(group + "-" + label)
        (test_wells if is_test else train_wells).add(group)
        # Label normal only before onset; omit the explicit 60-69 transition window.
        for start in range(0, len(frames), 10):
            segment = frames[start:start + 10]
            current_label = window_label(label, start)
            if current_label is None:
                continue
            target_rows.append(extract_features(segment))
            target_y.append(LABELS.index(current_label))
    x_train, x_test = np.array(train_rows), np.array(test_rows)
    y_train, y_test = np.array(train_y), np.array(test_y)
    mean, scale = x_train.mean(axis=0), x_train.std(axis=0)
    scale[scale == 0] = 1
    x_train, x_test = (x_train - mean) / scale, (x_test - mean) / scale
    weights = np.zeros((len(FEATURE_NAMES), len(LABELS)))
    bias = np.zeros(len(LABELS))
    onehot = np.eye(len(LABELS))[y_train]
    for _ in range(1200):
        logits = x_train @ weights + bias
        logits -= logits.max(axis=1, keepdims=True)
        probs = np.exp(logits); probs /= probs.sum(axis=1, keepdims=True)
        grad = (probs - onehot) / len(y_train)
        weights -= .08 * (x_train.T @ grad + .001 * weights)
        bias -= .08 * grad.sum(axis=0)
    pred = np.argmax(x_test @ weights + bias, axis=1)
    source = json.dumps({"version": GENERATOR_VERSION, "seed": SEED, "onset_frame": 60, "uncertain_frames": [60, 69], "window_frames": 10, "features": list(FEATURE_NAMES)}, sort_keys=True).encode()
    artifact = {"version": "softmax-v1", "feature_names": list(FEATURE_NAMES), "labels": list(LABELS),
                "mean": mean.tolist(), "scale": scale.tolist(), "weights": weights.tolist(), "bias": bias.tolist(),
                "dataset_generator": GENERATOR_VERSION, "dataset_seed": SEED, "dataset_spec_sha256": hashlib.sha256(source).hexdigest()}
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n")
    report = {"scope": "synthetic current-pattern classification only; not future incident prediction or field reliability",
              "limitations": ["generated telemetry, not observed field data", "well IDs are synthetic generator group keys, not independent real wells", "transition frames 60-69 are omitted; labels classify present patterns only", "no alert horizon, lead-time, operating-hour false-alert, or field validation"],
              "split": {"train_groups": len(train_groups), "test_groups": len(test_groups), "overlap_groups": len(train_groups & test_groups), "train_wells": len(train_wells), "test_wells": len(test_wells), "well_overlap": len(train_wells & test_wells), "train_windows": len(y_train), "test_windows": len(y_test)},
              "model": evaluate(y_test, pred), "majority_baseline": evaluate(y_test, np.full_like(y_test, np.bincount(y_train).argmax()))}
    report_path = ARTIFACT.with_name("evaluation.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"artifact": str(ARTIFACT), "evaluation": str(report_path), **report}, indent=2))


if __name__ == "__main__":
    main()
