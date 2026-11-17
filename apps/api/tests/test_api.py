import pytest
import os
import sys
import asyncio
import httpx

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.main import app
from apps.api.app.services.orchestrator import DomainOrchestrator

def run_async(coro):
    return asyncio.run(coro)


def reset_streams():
    DomainOrchestrator().stream_processors.clear()

def test_health_check():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "HEALTHY"
            assert "subsystems" in data
    run_async(_test())

def test_get_wells():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/wells")
            assert response.status_code == 200
            wells = response.json()
            assert len(wells) >= 1
            assert any(w["well_id"] == "NHK-421" for w in wells)
    run_async(_test())

def test_nearby_wells_radius_and_unknown_well():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            nearby = await client.get("/api/v1/wells/NHK-421/nearby", params={"radius_km": 2})
            assert nearby.status_code == 200
            candidates = nearby.json()
            assert [well["well_id"] for well in candidates] == ["NHK-412"]
            assert 0 < candidates[0]["distance_km"] < 2
            missing = await client.get("/api/v1/wells/UNKNOWN/nearby", params={"radius_km": 2})
            assert missing.status_code == 404
    run_async(_test())

def test_source_backed_formations_events_and_source_text():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            formations = await client.get("/api/v1/wells/NHK-412/formations")
            assert formations.status_code == 200
            rows = formations.json()
            barail = next(row for row in rows if row["formation_name"] == "Barail Coal-Shale")
            assert barail["md_top"] == 2540
            assert barail["md_bottom"] == 3390
            assert barail["tvd_top"] is None
            assert barail["source_file"] == "WCR_NHK_412.txt"

            events = await client.get("/api/v1/events", params={"well_id": "NHK-412"})
            event = events.json()[0]
            assert event["event_type"].startswith("GAS KICK")
            assert event["measured_depth_md_m"] == 2912
            assert event["source_file"] == "WCR_NHK_412.txt"
            assert event["page_marker"] == 24
            assert "18-barrel pit gain" in event["excerpt"]
            assert event["page_reference_type"] == "synthetic_text_report_marker_not_verified_pdf_page"

            source = await client.get("/api/v1/documents/WCR_NHK_412.txt/source")
            assert source.status_code == 200
            assert source.json()["physical_pdf_available"] is False
            assert "[PAGE 24]" in source.json()["text"]
            evidence = await client.get("/api/v1/documents/evidence", params={"well_id": "NHK-421", "depth": 2845})
            assert {record["document_name"] for record in evidence.json()} == {"WCR_MOR_118.txt", "WCR_NHK_412.txt"}
    run_async(_test())

def test_get_trajectory():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/wells/NHK-421/trajectory")
            assert response.status_code == 200
            stations = response.json()
            assert len(stations) >= 1
            assert stations[0]["measured_depth"] == 0.0
    run_async(_test())

def test_get_formations():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/wells/NHK-421/formations")
            assert response.status_code == 200
            formations = response.json()
            assert any(f["formation_name"] == "Barail Coal-Shale" for f in formations)
            assert all("SYNTHETIC DEMO PROGNOSIS" in f["method"] for f in formations)
    run_async(_test())


def test_historical_watch_is_formation_relative_and_radius_filtered():
    reset_streams()
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            nearby = await client.get("/api/v1/wells/NHK-421/historical-watch", params={"radius_km": 2})
            assert nearby.status_code == 200
            assert all(row["well_id"] == "NHK-412" for row in nearby.json())
            regional = await client.get("/api/v1/wells/NHK-421/historical-watch", params={"radius_km": 100})
            packoff = next(row for row in regional.json() if row["well_id"] == "MOR-118")
            assert packoff["illustrative_active_md_m"] == 2878.0
            assert packoff["distance_ahead_md_m"] > 0
            assert packoff["active_position_source"] == "synthetic demo progress marker"
            assert packoff["page_reference_type"] == "synthetic_text_report_marker_not_verified_pdf_page"
            assert "approximation" in packoff["alignment_method"]
    run_async(_test())


def test_telemetry_isolated_by_well_and_rejects_path_mismatch():
    reset_streams()
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            assert (await client.get("/api/v1/telemetry/NHK-421/latest")).status_code == 404
            active = {"timestamp": "2026-10-20T09:00:00Z", "well_id": "NHK-421", "measured_depth": 2845.1,
                      "bit_depth": 2844.9, "rop": 14.0, "wob": 12.0, "surface_torque": 14.2,
                      "rotary_rpm": 110, "standpipe_pressure": 2820.0, "flow_in": 2400.0,
                      "flow_out_pct": 100.0, "pit_volume": 42.0, "mud_weight_in": 1.28,
                      "ecd": 1.32, "gamma_ray": 85.0, "gas_total": 18.5}
            await client.post("/api/v1/telemetry/NHK-421/ingest", json=active)
            active = (await client.get("/api/v1/telemetry/NHK-421/latest")).json()
            other = await client.get("/api/v1/telemetry/NHK-412/latest")
            assert other.status_code == 404
            mismatch = await client.post("/api/v1/telemetry/NHK-412/ingest", json=active)
            assert mismatch.status_code == 422
            assert (await client.get("/api/v1/telemetry/NHK-421/latest")).json()["well_id"] == "NHK-421"
    run_async(_test())


def test_demo_reset_clears_buffers():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            frame = {"timestamp": "2026-10-20T09:00:00Z", "well_id": "NHK-421", "measured_depth": 2845.1,
                     "bit_depth": 2844.9, "rop": 14.0, "wob": 12.0, "surface_torque": 14.2,
                     "rotary_rpm": 110, "standpipe_pressure": 2820.0, "flow_in": 2400.0,
                     "flow_out_pct": 100.0, "pit_volume": 42.0, "mud_weight_in": 1.28,
                     "ecd": 1.32, "gamma_ray": 85.0, "gas_total": 18.5}
            await client.post("/api/v1/telemetry/NHK-421/ingest", json=frame)
            assert (await client.post("/api/v1/demo/reset")).json()["status"] == "RESET"
            assert (await client.get("/api/v1/telemetry/NHK-421/latest")).status_code == 404
    run_async(_test())

def test_get_current_risk():
    reset_streams()
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            assert (await client.get("/api/v1/risks/NHK-421/current")).status_code == 404
            frame = {"timestamp": "2026-10-20T09:00:00Z", "well_id": "NHK-421", "measured_depth": 2845.1,
                     "bit_depth": 2844.9, "rop": 14.0, "wob": 12.0, "surface_torque": 14.2,
                     "rotary_rpm": 110, "standpipe_pressure": 2820.0, "flow_in": 2400.0,
                     "flow_out_pct": 100.0, "pit_volume": 42.0, "mud_weight_in": 1.28,
                     "ecd": 1.32, "gamma_ray": 85.0, "gas_total": 18.5}
            await client.post("/api/v1/telemetry/NHK-421/ingest", json=frame)
            response = await client.get("/api/v1/risks/NHK-421/current")
            assert response.status_code == 200
            risk = response.json()
            assert "alert_type" in risk
            assert "severity" in risk
            assert "detailed_sop" in risk
    run_async(_test())

def test_assistant_chat():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "well_id": "NHK-421",
                "current_depth": 2845.0,
                "formation": "Barail Coal-Shale",
                "query": "What happened when MOR-118 stuck pipe in Barail coal?"
            }
            response = await client.post("/api/v1/assistant/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "citations" in data
            assert len(data["citations"]) >= 1
    run_async(_test())
