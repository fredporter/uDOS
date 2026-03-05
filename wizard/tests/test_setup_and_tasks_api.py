from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_routes import create_setup_routes
from wizard.routes.task_routes import create_task_routes


def build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(create_setup_routes(auth_guard=None))
    app.include_router(create_task_routes(auth_guard=None))
    return app


def test_setup_endpoints():
    app = build_app()
    client = TestClient(app)

    res = client.get("/api/setup/status")
    assert res.status_code == 200
    payload = res.json()
    assert "server" in payload
    assert "setup" in payload

    res = client.get("/api/setup/progress")
    assert res.status_code == 200
    payload = res.json()
    assert "progress_percent" in payload

    res = client.get("/api/setup/required-variables")
    assert res.status_code == 200
    payload = res.json()
    assert "variables" in payload

    res = client.post("/api/setup/wizard/start")
    assert res.status_code == 200

    res = client.post("/api/setup/wizard/complete")
    assert res.status_code == 200


def test_task_scheduler_status():
    app = build_app()
    client = TestClient(app)

    res = client.get("/api/tasks/status")
    assert res.status_code == 200
    payload = res.json()
    assert "settings" in payload
    assert "stats" in payload
    assert "queue" in payload

    res = client.post(
        "/api/tasks/schedule",
        json={"name": "Test Task", "cron_expression": "daily"},
    )
    assert res.status_code == 200

    res = client.get("/api/tasks/status")
    assert res.status_code == 200


def test_task_format_route_formats_contributor_tasks_payload():
    app = build_app()
    client = TestClient(app)

    res = client.post(
        "/api/tasks/format",
        json={
            "path": "dev/ops/tasks.json",
            "content": '{"updated":"2026-03-04","active_missions":[{"title":"Tracked editor","status":"done","id":"tracked-editor"}],"version":"1.0"}',
        },
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "ok"
    assert payload["format_helper"]["profile"] == "tasks-ledger"
    assert payload["content"].index('"version"') < payload["content"].index('"updated"')
