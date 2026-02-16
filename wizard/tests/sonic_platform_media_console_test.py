from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.platform_routes as platform_routes


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

    def set_reboot_route(self, profile_id, reason=None):
        return {"profile_id": profile_id, "reason": reason}


class _DeviceSvc:
    def get_recommendations(self):
        return {"profile": {"tier": "baseline"}, "recommendations": {"windows_mode": "media"}, "confidence": 0.5}


class _SyncSvc:
    def get_status(self):
        class _S:
            db_exists = True
            record_count = 0
            needs_rebuild = False
            last_sync = "2026-02-16T00:00:00Z"

        return _S()

    def rebuild_database(self, force=False):
        return {"status": "ok", "force": force}

    def export_to_csv(self, output_path=None):
        return {"status": "ok", "output_path": str(output_path) if output_path else "/tmp/sonic.csv"}


class _OpsSvc:
    available = True
    sync = _SyncSvc()


class _WindowsSvc:
    def get_status(self):
        return {"enabled": True, "mode": "media", "launcher": "kodi", "available_modes": ["media", "gaming", "install", "wtg"]}

    def set_mode(self, mode, launcher=None, auto_repair=None):
        return {"mode": mode, "launcher": launcher or "kodi", "auto_repair": True}


class _MediaSvc:
    active_launcher = None

    def list_launchers(self):
        return {
            "count": 2,
            "launchers": [{"id": "kodi"}, {"id": "wantmymtv"}],
            "status": self.get_status(),
        }

    def get_status(self):
        return {
            "supported_launchers": ["kodi", "wantmymtv"],
            "active_launcher": self.active_launcher,
            "running": self.active_launcher is not None,
        }

    def start(self, launcher):
        if launcher not in {"kodi", "wantmymtv"}:
            raise ValueError("Unsupported media launcher")
        self.active_launcher = launcher
        return {"active_launcher": launcher, "last_action": "start"}

    def stop(self):
        self.active_launcher = None
        return {"active_launcher": None, "last_action": "stop"}


def _client(monkeypatch):
    media = _MediaSvc()
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_boot_profile_service", lambda repo_root=None: _BootSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_device_profile_service", lambda repo_root=None: _DeviceSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _OpsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_launcher_service", lambda repo_root=None: _WindowsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_media_console_service", lambda repo_root=None: media)

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_sonic_media_console_workflows(monkeypatch):
    client = _client(monkeypatch)

    launchers = client.get("/api/platform/sonic/media/launchers")
    assert launchers.status_code == 200
    assert launchers.json()["count"] == 2

    start = client.post("/api/platform/sonic/media/start", json={"launcher": "kodi"})
    assert start.status_code == 200
    assert start.json()["state"]["active_launcher"] == "kodi"

    status = client.get("/api/platform/sonic/media/status")
    assert status.status_code == 200
    assert status.json()["running"] is True

    invalid = client.post("/api/platform/sonic/media/start", json={"launcher": "bad"})
    assert invalid.status_code == 400

    stop = client.post("/api/platform/sonic/media/stop")
    assert stop.status_code == 200
    assert stop.json()["state"]["active_launcher"] is None
