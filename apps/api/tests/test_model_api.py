import asyncio

import httpx

from apps.api.app.main import app


def test_model_report_and_classification_are_explicitly_experimental():
    async def check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            report = (await client.get("/api/v1/models/experimental")).json()
            assert report["enabled_for_alerts"] is False
            assert report["evaluation"]["split"]["overlap_groups"] == 0
            assert len(report["artifact_sha256"]) == 64
            await client.post("/api/v1/demo/replay", json={"scenario": "normal", "step": 10})
            result = await client.get("/api/v1/models/experimental/NHK-421/current")
            assert result.status_code == 200
            assert result.json()["enabled_for_alerts"] is False
            assert result.json()["label"] in ("normal", "packoff", "kick")
            await client.post("/api/v1/demo/reset")
            assert (await client.get("/api/v1/models/experimental/NHK-421/current")).status_code == 409
    asyncio.run(check())
