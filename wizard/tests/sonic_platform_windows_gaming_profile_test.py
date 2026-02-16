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


class _MediaSvc:
    def get_status(self):
        return {"running": False, "active_launcher": None}

    def list_launchers(self):
        return {"count": 2, "launchers": [{"id": "kodi"}, {"id": "wantmymtv"}], "status": self.get_status()}

    def start(self, launcher):
        return {"active_launcher": launcher}

    def stop(self):
        return {"active_launcher": None}


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


class _GamingSvc:
    def list_profiles(self):
        return {
            "count": 2,
            "profiles": [{"id": "performance"}, {"id": "balanced"}],
            "active": {"profile_id": "balanced"},
        }

    def apply_profile(self, profile_id, extra=None):
        if profile_id not in {"performance", "balanced"}:
            raise ValueError("Unsupported gaming profile")
        return {"profile_id": profile_id, "settings": extra or {}, "automation_status": "applied"}


def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_boot_profile_service", lambda repo_root=None: _BootSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_device_profile_service", lambda repo_root=None: _DeviceSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_media_console_service", lambda repo_root=None: _MediaSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _OpsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_launcher_service", lambda repo_root=None: _WindowsSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_windows_gaming_profile_service", lambda repo_root=None: _GamingSvc())

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_sonic_windows_gaming_profiles_and_apply(monkeypatch):
    client = _client(monkeypatch)

    profiles = client.get("/api/platform/sonic/windows/gaming/profiles")
    assert profiles.status_code == 200
    assert profiles.json()["count"] == 2

    apply_res = client.post(
        "/api/platform/sonic/windows/gaming/profiles/apply",
        json={"profile_id": "performance", "extra": {"fps_cap": 120}},
    )
    assert apply_res.status_code == 200
    assert apply_res.json()["profile"]["profile_id"] == "performance"
    assert apply_res.json()["profile"]["automation_status"] == "applied"

    invalid = client.post(
        "/api/platform/sonic/windows/gaming/profiles/apply",
        json={"profile_id": "unknown"},
    )
    assert invalid.status_code == 400
