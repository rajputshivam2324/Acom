"""
WebSocket API — real-time event stream for the frontend.
Broadcasts incident updates, timeline events, and telemetry changes.
"""
import asyncio
import json
import logging
from typing import Set
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger("acom.websocket")

router = APIRouter(tags=["WebSocket"])

# Connected clients
_clients: Set[WebSocket] = set()


async def broadcast(event_type: str, data: dict):
    """Broadcast an event to all connected WebSocket clients."""
    message = json.dumps({
        "type": event_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    disconnected = set()
    for ws in _clients:
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_text(message)
        except Exception:
            disconnected.add(ws)

    _clients.difference_update(disconnected)


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """Real-time event stream WebSocket endpoint."""
    await websocket.accept()
    _clients.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(_clients)}")

    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "data": {"message": "ACOM real-time event stream active"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))

        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Handle client pings
                if data == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }))
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }))
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        _clients.discard(websocket)
        logger.info(f"WebSocket client disconnected. Remaining: {len(_clients)}")
