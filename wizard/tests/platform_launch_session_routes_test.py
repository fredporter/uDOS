from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes
from wizard.services.sonic_media_console_service import SonicMediaConsoleService


class _BridgeSvc:
    def get_status(self):
        return {"available": True}

    def list_artifacts(self, limit=200):
        return {"available": True, "count": 0, "total_found": 0, "artifacts": []}


class _BuildSvc:
    def start_build(self, **_kwargs):
        return {"success": True}

    def list_builds(self, limit=50):
        return {"count": 0, "total_found": 0, "builds": []}

    def get_build(self, build_id):
        return {"build_id": build_id}

    def get_build_artifacts(self, build_id):
        return {"build_id": build_id, "artifacts": []}

    def get_release_readiness(self, build_id):
        return {"build_id": build_id, "release_ready": False, "issues": []}


class _BootSvc:
    def list_profiles(self):
        return {"profiles": [], "count": 0}

    def get_route_status(self):
        return {"active_route": None}


class _DeviceSvc:
    def get_recommendations(self):
        return {"profile": {"tier": "baseline"}, "recommendations": {}, "confidence": 0.5}


class _WindowsSvc:
    def get_status(self):
        return {"enabled": True, "mode": "media", "launcher": "kodi", "available_modes": ["media", "gaming", "install", "wtg"]}


class _GamingSvc:
    def list_profiles(self):
        return {"profiles": [], "count": 0}


class _OpsSvc:
    available = False


class _LinuxSvc:
    def get_status(self):
        return {"enabled": True}


def _client(monkeypatch, tmp_path):
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_boot_profile_service", lambda repo_root=None: _BootSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_device_profile_service", lambda repo_root=None: _DeviceSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_media_console_service", lambda repo_root=None: SonicMediaConsoleService(repo_root=tmp_path))
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _OpsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_launcher_service", lambda repo_root=None: _WindowsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_gaming_profile_service", lambda repo_root=None: _GamingSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_linux_launcher_service", lambda repo_root=None: _LinuxSvc())

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None, repo_root=tmp_path))
    return TestClient(app)


def test_launch_session_get_list_stream(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    started = client.post("/api/platform/sonic/media/start", json={"launcher": "kodi"})
    assert started.status_code == 200
    session_id = started.json()["state"]["session_id"]

    listed = client.get("/api/platform/launch/sessions", params={"target": "media-console"})
    assert listed.status_code == 200
    assert listed.json()["count"] >= 1

    session = client.get(f"/api/platform/launch/sessions/{session_id}")
    assert session.status_code == 200
    assert session.json()["session_id"] == session_id

    stream = client.get(f"/api/platform/launch/sessions/{session_id}/stream", params={"timeout_seconds": 5})
    assert stream.status_code == 200
    assert "event: session" in stream.text
    assert "event: end" in stream.text


def test_generic_launch_route(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    launched = client.post(
        "/api/platform/launch",
        json={
            "target": "alpine-core-one-app-shell",
            "mode": "gui",
            "launcher": "thin-gui",
            "workspace": "uhome",
            "profile_id": "server",
            "auth": {"wizard_mode_active": False},
            "portal_class": "private_resource_library",
            "library_kind": "markdown_vault",
        },
    )
    assert launched.status_code == 200
    body = launched.json()
    assert body["success"] is True
    assert body["session"]["target"] == "alpine-core-one-app-shell"
    assert body["state"]["portal_class"] == "private_resource_library"
    assert body["state"]["library_kind"] == "markdown_vault"
    assert "thin_gui" in body["state"]
