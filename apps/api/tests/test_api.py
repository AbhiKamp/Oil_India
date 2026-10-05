import pytest
import os
import sys
import asyncio
import httpx

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.main import app

def run_async(coro):
    return asyncio.run(coro)

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
            assert len(formations) >= 4
            assert any("Barail" in f["formation_name"] for f in formations)
    run_async(_test())

def test_get_current_risk():
    async def _test():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
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
