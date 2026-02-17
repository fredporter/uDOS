from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.dashboard_events_routes as dashboard_routes
from wizard.services.dashboard_events_service import DashboardEventsService


def _client(monkeypatch):
    service = DashboardEventsService()
    monkeypatch.setattr(dashboard_routes, "get_dashboard_events_service", lambda: service)
    app = FastAPI()
    app.include_router(dashboard_routes.create_dashboard_events_routes(auth_guard=None))
    return TestClient(app)


def test_dashboard_websocket_broadcast_and_status(monkeypatch):
    client = _client(monkeypatch)

    with client.websocket_connect("/api/dashboard/events/ws") as ws:
        hello = ws.receive_json()
        assert hello["type"] == "dashboard.connected"

        status_before = client.get("/api/dashboard/events/status")
        assert status_before.status_code == 200
        assert status_before.json()["active_connections"] == 1

        pushed = client.post(
            "/api/dashboard/events/broadcast",
            json={"event_type": "dashboard.snapshot", "payload": {"ok": True}},
        )
        assert pushed.status_code == 200
        assert pushed.json()["success"] is True

        event = ws.receive_json()
        assert event["type"] == "dashboard.snapshot"
        assert event["payload"]["ok"] is True

        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"

    status_after = client.get("/api/dashboard/events/status")
    assert status_after.status_code == 200
    assert status_after.json()["active_connections"] == 0
