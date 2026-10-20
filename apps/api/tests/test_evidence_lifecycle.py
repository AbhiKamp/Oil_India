"""Review decisions must change operational evidence, not just a badge in the UI."""

import asyncio

import httpx

from apps.api.app.main import app


def test_approval_and_rejection_change_retrieval_and_historical_watch(tmp_path, monkeypatch):
    monkeypatch.setenv("NWIS_DATA_DIR", str(tmp_path / "knowledge"))

    async def check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            text = b"Depth: 2,900 m MD | Formation: Barail Coal-Shale\nIncident Type: PACKOFF DEMO\nSynthetic laboratory event for source review.\n"
            response = await client.post("/api/v1/documents", files={"file": ("review.txt", text)},
                                         data={"well_id": "NHK-412", "provenance": "synthetic"})
            assert response.status_code == 200
            uploaded = response.json()
            event_id = uploaded["events"][0]["event_id"]

            async def visible_ids():
                watch = (await client.get("/api/v1/wells/NHK-421/historical-watch?radius_km=2")).json()
                evidence = (await client.get("/api/v1/documents/evidence?well_id=NHK-421&depth=2845")).json()
                return {row["event_id"] for row in watch}, {row["chunk_id"] for row in evidence}

            assert event_id not in (await visible_ids())[0]
            assert event_id not in (await visible_ids())[1]
            approved = await client.patch(f"/api/v1/events/{event_id}/review", json={
                "review_state": "approved", "reviewer": "Demo engineer"})
            assert approved.status_code == 200
            watch_ids, evidence_ids = await visible_ids()
            assert event_id in watch_ids and event_id in evidence_ids
            rejected = await client.patch(f"/api/v1/events/{event_id}/review", json={
                "review_state": "rejected", "reviewer": "Demo engineer"})
            assert rejected.status_code == 200
            watch_ids, evidence_ids = await visible_ids()
            assert event_id not in watch_ids and event_id not in evidence_ids

    asyncio.run(check())


def test_local_cors_does_not_allow_arbitrary_websites():
    async def check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.options("/api/v1/documents", headers={
                "Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"})
            assert response.status_code == 400
            assert "access-control-allow-origin" not in response.headers
            local = await client.options("/api/v1/documents", headers={
                "Origin": "http://127.0.0.1:41987", "Access-Control-Request-Method": "POST"})
            assert local.status_code == 200
            assert local.headers["access-control-allow-origin"] == "http://127.0.0.1:41987"

    asyncio.run(check())
