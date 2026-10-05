"""
StrataSentry-NWIS: WebSocket Live Streaming Endpoint
Streams continuous drilling sensor packets and real-time alerts to connected driller displays.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="", tags=["Streaming"])

@router.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    orc = DomainOrchestrator()
    try:
        while True:
            # Fetch latest frame and risk alert
            frame = orc.get_latest_telemetry()
            alert = orc.evaluate_live_risk(frame.get("well_id", "NHK-421"))

            payload = {
                "type": "TELEMETRY_UPDATE",
                "telemetry": frame,
                "current_risk": alert
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.0) # 1 Hz broadcast
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()
