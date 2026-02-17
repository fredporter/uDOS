"""Dashboard WebSocket event routes for real-time status push."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from wizard.services.dashboard_events_service import get_dashboard_events_service

AuthGuard = Optional[Callable]


class DashboardBroadcastRequest(BaseModel):
    event_type: str = Field(default="dashboard.update")
    payload: Dict[str, Any] = Field(default_factory=dict)


def create_dashboard_events_routes(auth_guard: AuthGuard = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/dashboard/events", tags=["dashboard-events"], dependencies=dependencies)
    service = get_dashboard_events_service()

    @router.get("/status")
    async def events_status() -> Dict[str, Any]:
        return {"success": True, **service.status()}

    @router.post("/broadcast")
    async def broadcast_event(payload: DashboardBroadcastRequest, request: Request) -> Dict[str, Any]:
        if auth_guard:
            maybe = auth_guard(request)
            if hasattr(maybe, "__await__"):
                await maybe
        summary = await service.broadcast(payload.event_type, payload.payload)
        return {"success": True, **summary}

    @router.websocket("/ws")
    async def websocket_events(websocket: WebSocket) -> None:
        await service.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                if not isinstance(data, dict):
                    continue
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "broadcast":
                    event_type = str(data.get("event_type") or "dashboard.client")
                    payload = data.get("payload") if isinstance(data.get("payload"), dict) else {}
                    await service.broadcast(event_type, payload)
        except WebSocketDisconnect:
            service.disconnect(websocket)
        except Exception:
            service.disconnect(websocket)
            return

    return router
