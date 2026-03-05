from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.renderer_routes as renderer_routes


def _client(monkeypatch) -> TestClient:
    app = FastAPI()
    app.include_router(renderer_routes.create_renderer_routes(auth_guard=None))
    return TestClient(app)


def test_renderer_render_response_includes_portal_metadata(monkeypatch):
    def _fake_invoke(theme: str, mission_id: str | None = None):
        return {
            "status": "completed",
            "job_id": "job_123",
            "mission_id": mission_id or "renderer-prose",
            "files": [{"path": "index.html", "size": 10, "updatedAt": "2026-01-01T00:00:00Z"}],
            "nav": [],
            "started_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:00:01Z",
        }

    monkeypatch.setattr(renderer_routes, "_invoke_renderer", _fake_invoke)
    client = _client(monkeypatch)

    response = client.post(
        "/api/renderer/render",
        json={
            "theme": "prose",
            "mission_id": "m1",
            "portal_class": "protected_portal",
            "auth_required": True,
            "library_kind": "markdown_vault",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["portal_class"] == "protected_portal"
    assert payload["auth_required"] is True
    assert payload["library_kind"] == "markdown_vault"
    assert payload["site_root"].endswith("/_site/prose")


def test_renderer_render_defaults_to_private_resource_library(monkeypatch):
    monkeypatch.setattr(
        renderer_routes,
        "_invoke_renderer",
        lambda theme, mission_id=None: {
            "status": "completed",
            "job_id": "job_124",
            "mission_id": mission_id or "renderer-prose",
            "files": [],
            "nav": [],
        },
    )
    client = _client(monkeypatch)

    response = client.post("/api/renderer/render", json={"theme": "prose"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["portal_class"] == "private_resource_library"
    assert payload["auth_required"] is True
    assert payload["library_kind"] == "markdown_vault"
