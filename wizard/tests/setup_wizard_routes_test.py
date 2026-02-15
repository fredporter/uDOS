from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_wizard_routes import create_setup_wizard_routes


def _result(data=None):
    return SimpleNamespace(data=data, locked=False, error=None)


def _build_app(**overrides):
    calls = overrides.setdefault("calls", {})

    def mark_setup_complete():
        calls["marked_complete"] = True

    router = create_setup_wizard_routes(
        get_status=overrides.get("get_status", lambda: {"setup_complete": False}),
        mark_setup_complete=overrides.get("mark_setup_complete", mark_setup_complete),
        validate_database_paths=overrides.get(
            "validate_database_paths", lambda: {"main": {"writable": True}}
        ),
        load_user_profile=overrides.get("load_user_profile", lambda: _result(data=None)),
        is_ghost_mode=overrides.get("is_ghost_mode", lambda username, role: False),
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/setup")
    return app, calls


def test_wizard_start_not_complete():
    app, _calls = _build_app(get_status=lambda: {"setup_complete": False, "initialized_at": "x"})
    client = TestClient(app)

    res = client.post("/api/setup/wizard/start")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "started"
    assert len(payload["steps"]) == 5


def test_wizard_start_already_complete():
    app, _calls = _build_app(
        get_status=lambda: {"setup_complete": True, "initialized_at": "2026-02-15T00:00:00Z"}
    )
    client = TestClient(app)

    res = client.post("/api/setup/wizard/start")
    assert res.status_code == 200
    assert res.json()["status"] == "already_complete"


def test_wizard_complete_success_marks_complete():
    app, calls = _build_app()
    client = TestClient(app)

    res = client.post("/api/setup/wizard/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "complete"
    assert calls["marked_complete"] is True


def test_wizard_complete_blocks_ghost_mode():
    app, _calls = _build_app(
        load_user_profile=lambda: _result(data={"username": "ghost", "role": "admin"}),
        is_ghost_mode=lambda username, role: True,
    )
    client = TestClient(app)

    res = client.post("/api/setup/wizard/complete")
    assert res.status_code == 400
    assert "Ghost Mode is active" in res.json()["detail"]
