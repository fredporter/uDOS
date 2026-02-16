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
        return {
            "name": "Sonic Boot Selector",
            "profiles": [
                {"id": "udos-alpine", "name": "uDOS Alpine Core"},
                {"id": "udos-windows-entertainment", "name": "Windows 10 Media & Entertainment"},
            ],
            "count": 2,
        }

    def get_route_status(self):
        return {"active_route": None, "state_path": "/tmp/boot-route.json"}

    def set_reboot_route(self, profile_id, reason=None):
        if profile_id not in {"udos-alpine", "udos-windows-entertainment"}:
            raise KeyError("Unknown boot profile")
        return {"profile_id": profile_id, "reason": reason or "manual route selection"}


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


def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_boot_profile_service", lambda repo_root=None: _BootSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _OpsSvc())
    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_sonic_boot_profile_and_reboot_route_endpoints(monkeypatch):
    client = _client(monkeypatch)

    profiles = client.get("/api/platform/sonic/boot/profiles")
    assert profiles.status_code == 200
    assert profiles.json()["count"] == 2

    status = client.get("/api/platform/sonic/boot/route")
    assert status.status_code == 200
    assert "active_route" in status.json()

    route = client.post(
        "/api/platform/sonic/boot/route",
        json={"profile_id": "udos-alpine", "reason": "test"},
    )
    assert route.status_code == 200
    assert route.json()["success"] is True
    assert route.json()["route"]["profile_id"] == "udos-alpine"

    missing = client.post("/api/platform/sonic/boot/route", json={"profile_id": "unknown"})
    assert missing.status_code == 404
