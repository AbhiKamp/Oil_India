"""Isolated experimental classifier; never used to raise operational alerts."""

import hashlib
import json

from fastapi import APIRouter, HTTPException

from models.experimental.classifier import ARTIFACT, load_model, predict
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/models/experimental", tags=["Synthetic ML Experiment"])


@router.get("")
async def model_report():
    try:
        model = load_model()
        evaluation = json.loads(ARTIFACT.with_name("evaluation.json").read_text())
    except (OSError, ValueError) as exc:
        raise HTTPException(503, "Experimental artifact or evaluation unavailable") from exc
    return {
        "method": "trained_numpy_softmax",
        "version": model["version"],
        "artifact_sha256": hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(),
        "enabled_for_alerts": False,
        "evaluation": evaluation,
        "limitation": "Synthetic current-pattern classification only; not a validated incident predictor.",
    }


@router.get("/{well_id}/current")
async def classify_current_window(well_id: str):
    try:
        window = DomainOrchestrator().processor_for(well_id).get_recent_history(10)
    except KeyError as exc:
        raise HTTPException(404, "Unknown well") from exc
    if len(window) < 2:
        raise HTTPException(409, "At least two timestamped replay samples are needed")
    try:
        result = predict(window, load_model())
    except (OSError, ValueError) as exc:
        raise HTTPException(409, "Classifier needs a valid artifact and increasing sample timestamps") from exc
    return {**result, "well_id": well_id, "enabled_for_alerts": False,
            "score_type": "uncalibrated_experimental_class_scores",
            "observation_timestamp": window[-1]["timestamp"]}
