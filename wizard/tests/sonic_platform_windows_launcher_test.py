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
        return {
            "enabled": True,
            "available_modes": ["gaming", "media", "install", "wtg"],
            "mode": "media",
            "launcher": "kodi",
        }

    def set_mode(self, mode, launcher=None, auto_repair=None):
        if mode not in {"gaming", "media", "install", "wtg"}:
            raise ValueError("Unsupported mode")
        return {
            "mode": mode,
            "launcher": launcher or "kodi",
            "auto_repair": True if auto_repair is None else auto_repair,
        }


def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_boot_profile_service", lambda repo_root=None: _BootSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _OpsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_launcher_service", lambda repo_root=None: _WindowsSvc())
    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_sonic_windows_launcher_status_and_mode_selector(monkeypatch):
    client = _client(monkeypatch)

    status = client.get("/api/platform/sonic/windows/launcher")
    assert status.status_code == 200
    payload = status.json()
    assert payload["enabled"] is True
    assert payload["mode"] == "media"

    set_mode = client.post(
        "/api/platform/sonic/windows/launcher/mode",
        json={"mode": "gaming", "launcher": "playnite"},
    )
    assert set_mode.status_code == 200
    assert set_mode.json()["state"]["mode"] == "gaming"
    assert set_mode.json()["state"]["launcher"] == "playnite"

    invalid = client.post("/api/platform/sonic/windows/launcher/mode", json={"mode": "unknown"})
    assert invalid.status_code == 400
