from fastapi import APIRouter, Body, HTTPException

from ..services import knowledge_store as store
from ..services.report_data import events as source_events

router = APIRouter(tags=["Engineer Decisions"])
STATUSES = {"acknowledged", "monitoring", "resolved"}


@router.get("/api/v1/decisions")
async def list_decisions(well_id: str | None = None):
    return store.decisions_for(well_id)


@router.post("/api/v1/decisions")
async def create_decision(payload: dict = Body(...)):
    if set(payload) != {"well_id", "event_id", "note", "actor", "status"}:
        raise HTTPException(422, "Expected well_id, event_id, note, actor, and status")
    well_id, event_id = payload["well_id"], payload["event_id"]
    note, actor, status = payload["note"], payload["actor"], payload["status"]
    if not isinstance(well_id, str) or not well_id.strip() or not isinstance(event_id, str) or not event_id:
        raise HTTPException(422, "well_id and event_id are required")
    if not isinstance(note, str) or not note.strip() or len(note) > 10000:
        raise HTTPException(422, "note must be non-blank and at most 10000 characters")
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 120:
        raise HTTPException(422, "actor must be non-blank and at most 120 characters")
    if not isinstance(status, str) or status not in STATUSES:
        raise HTTPException(422, "Invalid decision status")
    target_well_id = well_id.strip()
    event = store.event(event_id)
    if event is None:
        event = next((item for item in source_events() if item["event_id"] == event_id), None)
        if event:
            event.update({"review_state": "approved", "mitigation": None, "outcome": None})
            event.update(store.builtin_review(event_id) or {})
    if event is None:
        raise HTTPException(404, "Source event not found")
    if (target_well_id.casefold() not in store.known_wells() and
            target_well_id.casefold() != event["well_id"].casefold()):
        raise HTTPException(404, "Target well not found")
    if event.get("review_state") != "approved":
        raise HTTPException(409, "Only approved source events can be recorded as decisions")
    return store.save_decision(target_well_id, event, note.strip(), actor.strip(), status)
