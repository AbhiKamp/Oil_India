"""
StrataSentry-NWIS: Wells REST Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from math import asin, cos, radians, sin, sqrt
from typing import List
from ..schemas.pydantic_models import NearbyWellResponse, WellResponse
from ..services.orchestrator import DomainOrchestrator
from ..services.report_data import formations
from ..services.knowledge_store import list_events

router = APIRouter(prefix="/api/v1/wells", tags=["Wells"])

@router.get("", response_model=List[WellResponse])
async def list_wells():
    orc = DomainOrchestrator()
    return orc.wells

@router.get("/{well_id}", response_model=WellResponse)
async def get_well(well_id: str):
    orc = DomainOrchestrator()
    for w in orc.wells:
        if w["well_id"] == well_id or w["well_name"] == well_id:
            return w
    raise HTTPException(status_code=404, detail=f"Well {well_id} not found")


@router.get("/{well_id}/historical-watch")
async def historical_watch(well_id: str, radius_km: float = Query(default=50.0, gt=0, le=500)):
    """Formation-relative *illustrative* look-ahead; never a predicted incident."""
    if radius_km <= 0 or radius_km > 500:
        raise HTTPException(status_code=422, detail="radius_km must be in (0, 500]")
    orc = DomainOrchestrator()
    if well_id not in {well["well_id"] for well in orc.wells}:
        raise HTTPException(status_code=404, detail="Unknown well")
    active = formations(well_id) or []
    if not active:
        return []
    nearby = await nearby_wells(well_id, radius_km)
    current = orc.get_latest_telemetry(well_id).get("measured_depth")
    position_source = "synthetic telemetry snapshot"
    if current is None:
        active_well = next(well for well in orc.wells if well["well_id"] == well_id)
        current = active_well.get("current_depth_md")
        position_source = "synthetic demo progress marker"
    result = []
    for candidate in nearby:
        offsets = formations(candidate["well_id"]) or []
        for event in list_events(candidate["well_id"], review_state="approved"):
            depth = event["measured_depth_md_m"]
            if depth is None or not event["formation"]:
                continue
            name = event["formation"].casefold().removesuffix(" formation").strip()
            local = next((top for top in active if top["formation_name"].casefold() == name), None)
            offset = next((top for top in offsets if top["formation_name"].casefold() == name), None)
            if not local or not offset or not offset["md_top"] <= depth <= offset["md_bottom"]:
                continue
            equivalent = local["md_top"] + depth - offset["md_top"]
            if equivalent > local["md_bottom"]:
                continue
            result.append({
                **event,
                "surface_distance_km": candidate["distance_km"],
                "illustrative_active_md_m": round(equivalent, 1),
                "distance_ahead_md_m": round(equivalent - current, 1) if current is not None else None,
                "alignment_method": "formation-top-relative approximation against synthetic demo tops; not validated geological correlation",
                "active_position_source": position_source,
                "active_formation_source": local["source_file"],
                "offset_formation_source": offset["source_file"],
            })
    return sorted(result, key=lambda item: item["illustrative_active_md_m"])

@router.get("/{well_id}/nearby", response_model=List[NearbyWellResponse])
async def nearby_wells(well_id: str, radius_km: float = Query(gt=0, le=500)):
    wells = DomainOrchestrator().wells
    origin = next((w for w in wells if w["well_id"].casefold() == well_id.casefold()), None)
    if origin is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")

    def distance_km(well):
        lat1, lat2 = radians(origin["surface_latitude"]), radians(well["surface_latitude"])
        dlat = lat2 - lat1
        dlon = radians(well["surface_longitude"] - origin["surface_longitude"])
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6371.0088 * 2 * asin(sqrt(min(1.0, max(0.0, a))))

    found = []
    for well in wells:
        if well["well_id"] == origin["well_id"]:
            continue
        distance = distance_km(well)
        if distance <= radius_km:
            found.append({**{k: well[k] for k in ("well_id", "well_name", "field", "surface_latitude", "surface_longitude")}, "distance_km": round(distance, 3)})
    return sorted(found, key=lambda item: item["distance_km"])
