from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

import wizard.routes.platform_routes as platform_routes


class _BridgeSvc:
    def get_status(self):
        return {
            "available": True,
            "wizard_integrated": True,
            "version": "v1.3.17",
        }

    def list_artifacts(self, limit=200):
        return {"available": True, "count": 0, "total_found": 0, "artifacts": []}


class _BuildSvc:
    builds_root = "/tmp/builds"

    def start_build(self, profile="alpine-core+sonic", build_id=None, source_image=None, output_dir=None):
        return {"success": True, "build_id": build_id or "b1", "profile": profile}

    def list_builds(self, limit=5):
        return {"count": 1, "total_found": 1, "builds": [{"build_id": "b1", "profile": "alpine-core+sonic"}]}

    def get_build(self, build_id):
        return {"build_id": build_id}

    def get_build_artifacts(self, build_id):
        return {"build_id": build_id, "artifacts": []}

    def get_release_readiness(self, build_id):
        return {
            "build_id": build_id,
            "release_ready": True,
            "checksums": {"verified": True},
            "signing": {"ready": True},
            "issues": [],
        }


class _SyncStatus:
    db_exists = True
    record_count = 123
    needs_rebuild = False
    last_sync = "2026-02-16T00:00:00Z"


class _SyncSvc:
    def get_status(self):
        return _SyncStatus()

    def rebuild_database(self, force=False):
        return {"status": "ok", "force": force}

    def export_to_csv(self, output_path=None):
        return {"status": "ok", "output_path": str(output_path) if output_path else "/tmp/sonic.csv"}


class _SonicOps:
    available = True
    sync = _SyncSvc()


def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _SonicOps())
    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_sonic_gui_summary_and_actions(monkeypatch):
    client = _client(monkeypatch)

    summary_res = client.get("/api/platform/sonic/gui/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["sonic"]["available"] is True
    assert summary["dashboard"]["route"] == "#sonic"
    assert summary["latest_build"]["build_id"] == "b1"
    assert summary["latest_release_readiness"]["release_ready"] is True
    assert summary["release_signing_alert"] is None
    assert summary["dataset_contract"]["available"] is True
    assert "ok" in summary["dataset_contract"]
    assert "verification" in summary
    assert summary["sync_status"]["record_count"] == 123

    sync_res = client.post("/api/platform/sonic/gui/actions/sync", json={})
    assert sync_res.status_code == 200
    assert sync_res.json()["action"] == "sync"

    rebuild_res = client.post("/api/platform/sonic/gui/actions/rebuild", json={})
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["action"] == "rebuild"
    assert rebuild_res.json()["result"]["force"] is True

    export_res = client.post("/api/platform/sonic/gui/actions/export", json={"output_path": "/tmp/out.csv"})
    assert export_res.status_code == 200
    assert export_res.json()["action"] == "export"

    build_res = client.post("/api/platform/sonic/gui/actions/build", json={"profile": "alpine-core+sonic"})
    assert build_res.status_code == 200
    assert build_res.json()["action"] == "build"

    verify_res = client.get("/api/platform/sonic/verify")
    assert verify_res.status_code == 200
    assert "verification" in verify_res.json()


def test_sonic_gui_action_requires_plugin_for_sync(monkeypatch):
    class _UnavailableOps:
        available = False

    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _UnavailableOps())

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    client = TestClient(app)

    res = client.post("/api/platform/sonic/gui/actions/sync", json={})
    assert res.status_code == 503


def test_sonic_gui_summary_surfaces_signing_pubkey_alert(monkeypatch):
    class _WarnBuildSvc(_BuildSvc):
        def get_release_readiness(self, build_id):
            return {
                "build_id": build_id,
                "release_ready": False,
                "checksums": {"verified": True},
                "signing": {
                    "ready": False,
                    "manifest": {
                        "present": True,
                        "verified": False,
                        "detail": "WIZARD_SONIC_SIGN_PUBKEY not configured",
                    },
                    "checksums": {
                        "present": True,
                        "verified": False,
                        "detail": "WIZARD_SONIC_SIGN_PUBKEY not configured",
                    },
                },
                "issues": ["release signatures incomplete"],
            }

    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _WarnBuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _SonicOps())

    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    client = TestClient(app)

    summary = client.get("/api/platform/sonic/gui/summary").json()
    assert summary["release_signing_alert"]["code"] == "sonic_signing_pubkey_missing"
    assert summary["release_signing_alert"]["severity"] == "error"


def test_sonic_gui_summary_surfaces_dataset_contract_drift(monkeypatch):
    broken_verification = {
        "ok": False,
        "media_policy": {
            "policies": [
                {
                    "policy_id": "device-database",
                    "level": "error",
                    "detail": "Sonic dataset contract validation failed",
                    "contract": {
                        "ok": False,
                        "errors": ["schema version mismatch"],
                        "warnings": [],
                        "version": {"version": "v1.0.0", "schema_version": "9.9", "updated": "2026-03-02"},
                        "sql": {"seed_rows": [{"index": 1, "ok": False, "errors": ["seed row #1 mismatch"]}]},
                        "diff": {"required_mismatch_fields": ["year"]},
                    },
                }
            ]
        },
    }

    monkeypatch.setattr(platform_routes, "get_sonic_bridge_service", lambda repo_root=None: _BridgeSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_build_service", lambda repo_root=None: _BuildSvc())
    monkeypatch.setattr(platform_routes, "get_sonic_service", lambda repo_root=None: _SonicOps())

    app = FastAPI()
    with patch.object(platform_routes, "verify_sonic_ready", return_value=broken_verification):
        app.include_router(platform_routes.create_platform_routes(auth_guard=None))
        client = TestClient(app)
        summary = client.get("/api/platform/sonic/gui/summary").json()

    assert summary["dataset_contract"]["ok"] is False
    assert summary["dataset_contract"]["errors"] == ["schema version mismatch"]
    assert summary["dataset_contract"]["diff"]["required_mismatch_fields"] == ["year"]
