"""
Tests for dashboard summary / health aggregation routes.
"""
from __future__ import annotations

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.dashboard_summary_routes import create_dashboard_summary_routes


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(create_dashboard_summary_routes())
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/dashboard/health
# ---------------------------------------------------------------------------


def test_health_returns_200():
    client = _client()
    res = client.get("/api/dashboard/health")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["bridge"] == "udos-wizard"
    assert "version" in body
    assert "timestamp" in body
    assert "logic_local_ready" in body


def test_health_logic_local_ready_true(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(
        mod, "_logic_local_status",
        lambda: {"ready": True, "runtime": "gpt4all", "model": "devstral-small-2.gguf"},
    )
    body = _client().get("/api/dashboard/health").json()
    assert body["logic_local_ready"] is True


def test_health_logic_local_ready_false(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_logic_local_status", lambda: {"ready": False})
    body = _client().get("/api/dashboard/health").json()
    assert body["logic_local_ready"] is False


# ---------------------------------------------------------------------------
# GET /api/dashboard/summary
# ---------------------------------------------------------------------------


def _patch_all_healthy(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(
        mod,
        "_logic_local_status",
        lambda: {"ready": True, "runtime": "gpt4all", "model": "devstral-small-2.gguf"},
    )
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": ["mistral"], "primary": "mistral"})
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": True, "status": "ok"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    monkeypatch.setattr(mod, "get_repo_root", lambda: "/tmp/udos")
    monkeypatch.setattr(
        mod,
        "get_template_workspace_service",
        lambda repo_root=None: type(
            "_Workspace",
            (),
            {
                "component_contract": lambda self, component_id: {
                    "component_id": component_id,
                    "workspace_ref": "@memory/bank/typo-workspace",
                },
                "component_snapshot": lambda self, component_id: {
                    "component_id": component_id,
                    "settings": {"effective_source": "user"},
                },
            },
        )(),
    )
    monkeypatch.setattr(
        mod,
        "get_sonic_build_service",
        lambda repo_root=None: type(
            "_BuildSvc",
            (),
            {
                "default_profile": "alpine-core+sonic",
                "default_profile_source": "template_workspace",
            },
        )(),
    )
    monkeypatch.setattr(
        mod,
        "get_sonic_media_console_service",
        lambda repo_root=None: type(
            "_MediaSvc",
            (),
            {
                "get_status": lambda self: {
                    "preferred_launcher": "kodi",
                    "preferred_launcher_source": "template_workspace",
                }
            },
        )(),
    )
    monkeypatch.setattr(
        mod,
        "get_sonic_boot_profile_service",
        lambda repo_root=None: type(
            "_BootSvc",
            (),
            {
                "get_route_status": lambda self: {
                    "preferred_route_profile_id": "udos-alpine",
                    "preferred_route_source": "template_workspace",
                    "preferred_route": {"id": "udos-alpine", "name": "uDOS Alpine Core"},
                }
            },
        )(),
    )
    monkeypatch.setattr(
        mod,
        "get_uhome_presentation_service",
        lambda repo_root=None: type(
            "_UHomeSvc",
            (),
            {
                "get_status": lambda self: {
                    "preferred_presentation": "thin-gui",
                    "preferred_presentation_source": "template_workspace",
                    "node_role": "server",
                    "node_role_source": "template_workspace",
                }
            },
        )(),
    )


def test_summary_returns_200(monkeypatch):
    _patch_all_healthy(monkeypatch)
    res = _client().get("/api/dashboard/summary")
    assert res.status_code == 200


def test_summary_shape(monkeypatch):
    _patch_all_healthy(monkeypatch)
    body = _client().get("/api/dashboard/summary").json()
    assert body["ok"] is True
    assert "subsystems" in body
    assert "summary" in body
    assert set(body["subsystems"].keys()) == {
        "logic_local",
        "cloud",
        "ha_bridge",
        "secret_sync",
        "workspace_runtime",
    }


def test_summary_all_healthy(monkeypatch):
    _patch_all_healthy(monkeypatch)
    body = _client().get("/api/dashboard/summary").json()
    assert body["summary"]["healthy"] == 5
    assert body["summary"]["degraded"] == 0


def test_summary_includes_workspace_runtime_defaults(monkeypatch):
    _patch_all_healthy(monkeypatch)
    body = _client().get("/api/dashboard/summary").json()
    runtime = body["workspace_runtime"]

    assert runtime["ok"] is True
    assert runtime["workspace_ref"] == "@memory/bank/typo-workspace"
    assert runtime["components"]["sonic"]["defaults"]["build_profile"]["value"] == "alpine-core+sonic"
    assert runtime["components"]["sonic"]["defaults"]["boot_route"]["value"] == "udos-alpine"
    assert runtime["components"]["sonic"]["defaults"]["media_launcher"]["value"] == "kodi"
    assert runtime["components"]["uhome"]["defaults"]["presentation"]["value"] == "thin-gui"
    assert runtime["components"]["uhome"]["defaults"]["node_role"]["value"] == "server"


def test_summary_overall_ok_false_when_logic_local_down(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_logic_local_status", lambda: (_ for _ in ()).throw(RuntimeError("model missing")))
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": [], "primary": None})
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": False, "status": "disabled"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    body = _client().get("/api/dashboard/summary").json()
    assert body["ok"] is False
    assert body["subsystems"]["logic_local"]["ok"] is False


def test_summary_non_critical_failure_does_not_degrade_ok(monkeypatch):
    """HA bridge down or secret sync failing doesn't mark overall ok=False."""
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_logic_local_status", lambda: {"ready": True, "runtime": "gpt4all"})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": ["mistral"], "primary": "mistral"})
    # Non-critical subsystems raise
    monkeypatch.setattr(mod, "_ha_status", lambda: (_ for _ in ()).throw(RuntimeError("bridge offline")))
    monkeypatch.setattr(mod, "_sync_status", lambda: (_ for _ in ()).throw(RuntimeError("vault locked")))
    body = _client().get("/api/dashboard/summary").json()
    assert body["ok"] is True  # critical subsystems are fine
    assert body["subsystems"]["ha_bridge"]["ok"] is False
    assert body["subsystems"]["secret_sync"]["ok"] is False
    assert body["summary"]["degraded"] == 2


def test_summary_subsystem_error_propagates_message(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_logic_local_status", lambda: {"ready": True})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": False, "available_providers": [], "primary": None})
    monkeypatch.setattr(mod, "_ha_status", lambda: (_ for _ in ()).throw(ConnectionError("ha unreachable")))
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    body = _client().get("/api/dashboard/summary").json()
    ha = body["subsystems"]["ha_bridge"]
    assert ha["ok"] is False
    assert "ha unreachable" in ha["error"]


def test_summary_cloud_details_exposed(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_logic_local_status", lambda: {"ready": True})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {
        "ready": True, "available_providers": ["mistral", "openai"], "primary": "mistral"
    })
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": True, "status": "ok"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {"drift_issues": 0, "issues": [], "synced": True})
    body = _client().get("/api/dashboard/summary").json()
    cloud = body["subsystems"]["cloud"]
    assert cloud["primary"] == "mistral"
    assert "openai" in cloud["available_providers"]


def test_summary_sync_drift_reported(monkeypatch):
    import wizard.routes.dashboard_summary_routes as mod
    monkeypatch.setattr(mod, "_logic_local_status", lambda: {"ready": True})
    monkeypatch.setattr(mod, "_cloud_status", lambda: {"ready": True, "available_providers": [], "primary": None})
    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": False, "status": "disabled"})
    monkeypatch.setattr(mod, "_sync_status", lambda: {
        "drift_issues": 2,
        "issues": ["missing_wizard_key", "missing_admin_token"],
        "synced": False,
    })
    body = _client().get("/api/dashboard/summary").json()
    sync = body["subsystems"]["secret_sync"]
    assert sync["drift_issues"] == 2
    assert "missing_wizard_key" in sync["issues"]
