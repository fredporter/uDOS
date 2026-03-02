from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.ops_routes as ops_routes_module
import wizard.services.store as store_module
import wizard.services.task_scheduler as task_scheduler_module
from wizard.routes.ops_routes import create_ops_routes
from wizard.services.task_scheduler import TaskScheduler


def _build_app(tmp_path: Path, monkeypatch):
    store_module._STORE = None
    monkeypatch.setattr(store_module, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(task_scheduler_module, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(ops_routes_module, "get_repo_root", lambda: tmp_path)
    app = FastAPI()
    app.include_router(
        create_ops_routes(
            auth_guard=None,
            session_resolver=lambda _request: {
                "subject": "user-1",
                "email": "user@example.com",
                "display_name": "User",
                "role": "admin",
            },
        )
    )
    return app


def test_ops_session_and_releases_routes(tmp_path, monkeypatch):
    client = TestClient(_build_app(tmp_path, monkeypatch))

    session_res = client.get("/api/ops/session")
    assert session_res.status_code == 200
    assert session_res.json()["authenticated"] is True

    releases_res = client.get("/api/ops/releases")
    assert releases_res.status_code == 200
    assert "workflows" in releases_res.json()


def test_ops_jobs_and_config_status_routes(tmp_path, monkeypatch):
    client = TestClient(_build_app(tmp_path, monkeypatch))

    create_res = client.post(
        "/api/ops/jobs",
        json={
            "name": "Nightly workflow window",
            "schedule": "daily",
            "kind": "window",
            "project": "ops-calendar",
            "window": "off_peak",
            "budget_units": 4,
        },
    )
    assert create_res.status_code == 200
    assert create_res.json()["created"][0]["name"] == "Nightly workflow window"
    assert create_res.json()["created"][0]["payload"]["project"] == "ops-calendar"
    assert create_res.json()["created"][0]["payload"]["window"] == "off_peak"
    job_id = create_res.json()["created"][0]["id"]

    scheduler = TaskScheduler()
    scheduler.schedule_task(job_id, datetime.now())

    jobs_res = client.get("/api/ops/jobs")
    assert jobs_res.status_code == 200
    assert "runtime" in jobs_res.json()
    assert "server_time" in jobs_res.json()["runtime"]
    assert "tasks" in jobs_res.json()
    assert "workspace_sources" in jobs_res.json()
    assert "settings" in jobs_res.json()

    queue_item = next(item for item in jobs_res.json()["queue"] if item["task_id"] == job_id)
    queue_id = queue_item["id"]
    retry_res = client.post(f"/api/ops/jobs/queue/{queue_id}/retry")
    assert retry_res.status_code == 200
    assert retry_res.json()["success"] is True
    assert retry_res.json()["queue_item"]["defer_reason"] is None
    assert retry_res.json()["queue_item"]["defer_count"] == 0

    scheduler.release_queue_item(queue_id, reason="network_unavailable", backoff_seconds=300)

    preview_res = client.get("/api/ops/jobs/deferred-preview?reason=network_unavailable&limit=5")
    assert preview_res.status_code == 200
    assert preview_res.json()["count"] == 1
    assert preview_res.json()["queue_items"][0]["id"] == queue_id

    bulk_retry_res = client.post("/api/ops/jobs/retry-deferred?reason=network_unavailable&limit=5")
    assert bulk_retry_res.status_code == 200
    assert bulk_retry_res.json()["success"] is True
    assert bulk_retry_res.json()["count"] == 1
    assert bulk_retry_res.json()["queue_items"][0]["defer_reason"] is None

    summary_res = client.get("/api/ops/summary")
    assert summary_res.status_code == 200
    assert "automation" in summary_res.json()
    assert "recent_runs" in summary_res.json()["automation"]
    assert "status" in summary_res.json()["automation"]
    assert "runtime" in summary_res.json()
    assert "server_time" in summary_res.json()["runtime"]
    assert "local_time" in summary_res.json()["runtime"]["server_time"]
    assert "offset" in summary_res.json()["runtime"]["server_time"]

    health_res = client.get("/api/ops/health")
    assert health_res.status_code == 200
    assert "runtime" in health_res.json()
    assert "server_time" in health_res.json()["runtime"]

    settings_res = client.post("/api/ops/settings", json={"api_budget_daily": 12, "off_peak_start_hour": 19})
    assert settings_res.status_code == 200
    assert settings_res.json()["settings"]["api_budget_daily"] == 12

    backoff_res = client.post(
        "/api/ops/settings",
        json={
            "backoff_policy": {
                "resource_pressure": {"base_minutes": 5, "max_minutes": 45},
                "network_unavailable": {"base_minutes": 3, "max_minutes": 30},
            }
        },
    )
    assert backoff_res.status_code == 200
    assert backoff_res.json()["settings"]["backoff_policy"]["resource_pressure"]["base_minutes"] == 5
    assert backoff_res.json()["settings"]["backoff_policy"]["resource_pressure"]["max_minutes"] == 45

    maintenance_policy_res = client.post(
        "/api/ops/settings",
        json={
            "maintenance_retry_dry_run": True,
            "auto_retry_deferred_policy": {
                "network_unavailable": {"enabled": True, "limit": 3, "dry_run": False},
                "api_budget_exhausted": {"enabled": True, "limit": 2, "dry_run": True},
            },
        },
    )
    assert maintenance_policy_res.status_code == 200
    assert maintenance_policy_res.json()["settings"]["maintenance_retry_dry_run"] is True
    assert maintenance_policy_res.json()["settings"]["auto_retry_deferred_policy"]["network_unavailable"]["limit"] == 3

    invalid_policy_res = client.post(
        "/api/ops/settings",
        json={
            "auto_retry_deferred_policy": {
                "network_unavailable": {"enabled": True, "limit": -1, "dry_run": False},
            },
        },
    )
    assert invalid_policy_res.status_code == 400
    assert "invalid limit" in invalid_policy_res.json()["detail"].lower()

    invalid_window_res = client.post(
        "/api/ops/settings",
        json={
            "auto_retry_deferred_policy": {
                "network_unavailable": {"enabled": True, "limit": 1, "dry_run": False, "window": "bad-window"},
            },
        },
    )
    assert invalid_window_res.status_code == 400
    assert "invalid window" in invalid_window_res.json()["detail"].lower()

    config_res = client.get("/api/ops/config-status")
    assert config_res.status_code == 200
    assert "managed_contract" in config_res.json()
