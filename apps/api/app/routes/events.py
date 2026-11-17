import math

from fastapi import APIRouter, Body, HTTPException

from ..services import knowledge_store as store
from ..services.report_data import events as source_events, reports

router = APIRouter(tags=["Historical Events"])


@router.get("/api/v1/events")
async def list_events(well_id: str | None = None, q: str | None = None,
                      review_state: str | None = None):
    if well_id and well_id.casefold() not in {key.casefold() for key in reports()}:
        # Uploaded-only wells remain searchable.
        if not any(row["well_name"].casefold() == well_id.casefold() for row in store.uploaded_documents()):
            raise HTTPException(status_code=404, detail=f"Well {well_id} has no source report")
    return store.list_events(well_id, q, review_state)


@router.patch("/api/v1/events/{event_id}/review")
async def review_event(event_id: str, payload: dict = Body(...)):
    allowed = {"review_state", "reviewer", "event_type", "formation", "measured_depth_md_m"}
    if set(payload) - allowed:
        raise HTTPException(422, "Unsupported review fields")
    reviewer = payload.get("reviewer")
    state = payload.get("review_state")
    if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 120:
        raise HTTPException(422, "reviewer is required")
    if not isinstance(state, str) or state not in {"approved", "needs_review", "rejected"}:
        raise HTTPException(422, "Invalid review_state")
    changes = {key: payload[key] for key in ("review_state", "event_type", "formation", "measured_depth_md_m")
               if key in payload}
    if "event_type" in changes and (not isinstance(changes["event_type"], str) or
                                    not changes["event_type"].strip() or len(changes["event_type"]) > 200):
        raise HTTPException(422, "event_type must be a non-empty string up to 200 characters")
    if "formation" in changes and changes["formation"] is not None and (
            not isinstance(changes["formation"], str) or len(changes["formation"]) > 200):
        raise HTTPException(422, "formation must be text or null")
    depth = changes.get("measured_depth_md_m")
    if depth is not None and (isinstance(depth, bool) or not isinstance(depth, (int, float)) or
                              not math.isfinite(depth) or depth < 0 or depth > 100000):
        raise HTTPException(422, "measured_depth_md_m must be a finite non-negative metre value")
    base = next((item for item in source_events() if item["event_id"] == event_id), None)
    if base:
        base.update({"review_state": "approved", "provenance": "synthetic"})
        base.update(store.builtin_review(event_id) or {})
    updated = store.save_review(event_id, changes, reviewer.strip(), base)
    if updated is None:
        raise HTTPException(404, "Event not found")
    return updated
