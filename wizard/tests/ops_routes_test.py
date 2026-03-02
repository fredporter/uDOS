from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.ops_routes import create_ops_routes


def _build_app():
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


def test_ops_session_and_releases_routes():
    client = TestClient(_build_app())

    session_res = client.get("/api/ops/session")
    assert session_res.status_code == 200
    assert session_res.json()["authenticated"] is True

    releases_res = client.get("/api/ops/releases")
    assert releases_res.status_code == 200
    assert "workflows" in releases_res.json()


def test_ops_jobs_and_config_status_routes():
    client = TestClient(_build_app())

    create_res = client.post(
        "/api/ops/jobs",
        json={"name": "Nightly workflow window", "schedule": "daily", "kind": "window"},
    )
    assert create_res.status_code == 200
    assert create_res.json()["created"][0]["name"] == "Nightly workflow window"

    jobs_res = client.get("/api/ops/jobs")
    assert jobs_res.status_code == 200
    assert "tasks" in jobs_res.json()
    assert "workspace_sources" in jobs_res.json()

    config_res = client.get("/api/ops/config-status")
    assert config_res.status_code == 200
    assert "managed_contract" in config_res.json()
