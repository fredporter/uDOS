import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_core_routes import create_setup_core_routes


def _build_app(calls):
    def get_status():
        return {
            "setup_complete": False,
            "initialized_at": "2026-02-15T00:00:00Z",
            "variables_configured": ["user_profile"],
            "services_enabled": ["wizard"],
            "steps_completed": [1],
        }

    def get_required_variables():
        return {
            "a": {"required": True},
            "b": {"required": False},
            "c": {"required": True},
        }

    router = create_setup_core_routes(
        get_full_config_status=lambda: {"server": {"ok": True}, "setup": {"ok": True}},
        get_status=get_status,
        get_required_variables=get_required_variables,
        mark_variable_configured=lambda name: calls.setdefault("marked_vars", []).append(name),
        mark_step_complete=lambda step_id, completed: calls.setdefault("marked_steps", []).append(
            {"step_id": step_id, "completed": completed}
        ),
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/setup")
    return app


def test_status_progress_and_required_variables():
    calls = {}
    app = _build_app(calls)
    client = TestClient(app)

    res_status = client.get("/api/setup/status")
    assert res_status.status_code == 200
    assert "server" in res_status.json()

    res_progress = client.get("/api/setup/progress")
    assert res_progress.status_code == 200
    progress = res_progress.json()
    assert progress["required_variables"] == 2
    assert progress["variables_configured"] == 1

    res_required = client.get("/api/setup/required-variables")
    assert res_required.status_code == 200
    assert "variables" in res_required.json()


def test_configure_marks_variable():
    calls = {}
    app = _build_app(calls)
    client = TestClient(app)

    prev = os.environ.get("TEST_SETUP_VAR")
    try:
        res = client.post(
            "/api/setup/configure",
            json={"name": "test_setup_var", "value": "1"},
        )
        assert res.status_code == 200
        assert os.environ.get("TEST_SETUP_VAR") == "1"
        assert calls["marked_vars"] == ["test_setup_var"]
    finally:
        if prev is None:
            os.environ.pop("TEST_SETUP_VAR", None)
        else:
            os.environ["TEST_SETUP_VAR"] = prev


def test_step_complete_marks_step():
    calls = {}
    app = _build_app(calls)
    client = TestClient(app)

    res = client.post("/api/setup/steps/complete", json={"step_id": 2, "completed": True})
    assert res.status_code == 200
    assert calls["marked_steps"][0]["step_id"] == 2
    assert calls["marked_steps"][0]["completed"] is True
