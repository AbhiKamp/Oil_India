from datetime import datetime, timedelta, timezone

import pytest

from models.experimental.classifier import ARTIFACT, extract_features, load_model, predict
from models.experimental.train import generate, split_group_indices, window_label


def test_extractor_uses_timestamp_delta_and_rejects_invalid_time():
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    rows = [{"timestamp": (start + timedelta(seconds=i * 2)).isoformat(), "standpipe_pressure": i * 10,
             "rop": 5, "surface_torque": 8, "pit_volume": i * 4, "flow_out_pct": 70} for i in range(3)]
    features = extract_features(rows)
    assert features[1] == pytest.approx(5)
    assert features[4] == pytest.approx(2)
    rows[2]["timestamp"] = rows[1]["timestamp"]
    with pytest.raises(ValueError, match="strictly increasing"):
        extract_features(rows)


def test_generated_trace_groups_are_split_before_windows():
    groups = generate()
    assert groups == generate()
    train_ids, test_ids = split_group_indices(10)
    train_wells = {groups[i][0] for i in range(len(groups)) if int(groups[i][0][4:]) in train_ids}
    test_wells = {groups[i][0] for i in range(len(groups)) if int(groups[i][0][4:]) in test_ids}
    assert train_wells.isdisjoint(test_wells)
    assert len(train_ids) == 8 and len(test_ids) == 2
    assert all(len(frames) == 100 for _, _, frames in groups)


def test_pre_onset_scenario_windows_are_labeled_normal():
    groups = generate()
    for _, label, frames in groups:
        if label in ("packoff", "kick"):
            assert [window_label(label, start) for start in (0, 50, 60, 70)] == ["normal", "normal", None, label]


def test_missing_model_is_explicit(tmp_path):
    with pytest.raises(FileNotFoundError, match="artifact missing"):
        load_model(tmp_path / "missing.json")


def test_trained_artifact_inference():
    model = load_model(ARTIFACT)
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    frames = [{"timestamp": (start + timedelta(seconds=i)).isoformat(), "standpipe_pressure": 2800 + i,
               "rop": 10, "surface_torque": 15, "pit_volume": 40 + i * .01, "flow_out_pct": 75} for i in range(10)]
    result = predict(frames, model)
    assert result["label"] in ("normal", "packoff", "kick")
    assert sum(result["scores"].values()) == pytest.approx(1)


def test_model_loader_rejects_bad_shapes_and_scales(tmp_path):
    import json

    model = load_model(ARTIFACT)
    model["scale"][0] = 0
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(model))
    with pytest.raises(ValueError, match="finite and scales positive"):
        load_model(broken)
