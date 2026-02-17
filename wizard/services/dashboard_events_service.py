"""Dashboard WebSocket event fanout service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class DashboardEventsService:
    """Manages dashboard WebSocket clients and event broadcasts."""

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._last_event: Optional[Dict[str, Any]] = None
        self._events_sent = 0

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        await websocket.send_json(
            {
                "type": "dashboard.connected",
                "timestamp": _utc_now(),
                "active_connections": len(self._connections),
            }
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = {
            "type": event_type,
            "timestamp": _utc_now(),
            "payload": payload,
        }
        stale: Set[WebSocket] = set()
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception:
                stale.add(ws)
        for ws in stale:
            self._connections.discard(ws)
        self._last_event = message
        self._events_sent += 1
        return {
            "active_connections": len(self._connections),
            "events_sent": self._events_sent,
            "last_event": self._last_event,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "active_connections": len(self._connections),
            "events_sent": self._events_sent,
            "last_event": self._last_event,
        }


_dashboard_events_service: Optional[DashboardEventsService] = None


def get_dashboard_events_service() -> DashboardEventsService:
    global _dashboard_events_service
    if _dashboard_events_service is None:
        _dashboard_events_service = DashboardEventsService()
    return _dashboard_events_service
