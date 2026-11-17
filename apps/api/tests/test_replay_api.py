import asyncio
import httpx

from apps.api.app.main import app


def test_replay_seek_is_deterministic_and_rejects_invalid_input():
    async def check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            first = (await client.post("/api/v1/demo/replay", json={"scenario": "packoff", "step": 50})).json()
            normal = (await client.post("/api/v1/demo/replay", json={"scenario": "normal", "step": 50})).json()
            assert first["telemetry"]["standpipe_pressure"] > normal["telemetry"]["standpipe_pressure"]
            assert normal["risk"]["severity"] in ("INFO", "WATCH")
            again = (await client.post("/api/v1/demo/replay", json={"scenario": "packoff", "step": 50})).json()
            assert first["telemetry"] == again["telemetry"]
            assert first["risk"]["alert_id"] == again["risk"]["alert_id"]
            assert first["risk"]["numeric_score_type"] == "uncalibrated_heuristic_score"
            repeated = await client.post("/api/v1/telemetry/NHK-421/ingest", json=first["telemetry"])
            assert repeated.status_code == 409
            empty = (await client.post("/api/v1/demo/replay", json={"step": 0})).json()
            assert empty["telemetry"] is None and empty["risk"] is None
            for invalid in ({"step": -1}, {"step": 81}, {"scenario": "loss"}, {"well_id": "UNKNOWN"}):
                assert (await client.post("/api/v1/demo/replay", json=invalid)).status_code == 422
            assert (await client.post("/api/v1/telemetry/NHK-421/ingest", json={"well_id": "NHK-421"})).status_code == 422
            assert (await client.get("/api/v1/telemetry/NHK-421/history?limit=-1")).status_code == 422
    asyncio.run(check())
