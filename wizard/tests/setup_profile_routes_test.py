from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.setup_profile_routes import create_setup_profile_routes


def _result(data=None, locked=False, error=None):
    return SimpleNamespace(data=data, locked=locked, error=error)


def _build_app(**overrides):
    calls = overrides.setdefault("calls", {})
    user_data = overrides.get("user_data", {"username": "alice", "role": "admin"})
    install_data = overrides.get("install_data", {"installation_id": "inst-1"})

    def load_user_profile():
        return _result(data=user_data)

    def load_install_profile():
        return _result(data=install_data)

    def save_user_profile(payload):
        calls["saved_user"] = payload
        return _result(data=payload)

    def save_install_profile(payload):
        calls["saved_install"] = payload
        return _result(data=payload)

    router = create_setup_profile_routes(
        load_user_profile=overrides.get("load_user_profile", load_user_profile),
        load_install_profile=overrides.get("load_install_profile", load_install_profile),
        save_user_profile=overrides.get("save_user_profile", save_user_profile),
        save_install_profile=overrides.get("save_install_profile", save_install_profile),
        load_install_metrics=overrides.get("load_install_metrics", lambda: {"moves_used": 0}),
        sync_metrics_from_profile=overrides.get(
            "sync_metrics_from_profile", lambda profile: {"moves_used": 1}
        ),
        increment_moves=overrides.get("increment_moves", lambda: {"moves_used": 2}),
        mark_variable_configured=overrides.get(
            "mark_variable_configured", lambda name: calls.setdefault("marked", []).append(name)
        ),
        apply_capabilities_to_wizard_config=overrides.get(
            "apply_capabilities_to_wizard_config",
            lambda capabilities: calls.setdefault("applied_caps", []).append(capabilities),
        ),
        validate_location_id=overrides.get(
            "validate_location_id", lambda location_id: calls.setdefault("validated", []).append(location_id)
        ),
        resolve_location_name=overrides.get(
            "resolve_location_name", lambda location_id: f"Name-{location_id}"
        ),
        is_ghost_mode=overrides.get("is_ghost_mode", lambda username, role: False),
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/setup")
    return app, calls


def test_set_user_profile_marks_state_and_resolves_location():
    app, calls = _build_app()
    client = TestClient(app)

    res = client.post(
        "/api/setup/profile/user",
        json={
            "username": "alice",
            "date_of_birth": "2000-01-01",
            "role": "admin",
            "timezone": "UTC",
            "local_time": "2026-01-01 10:00",
            "location_id": "L-1",
            "permissions": {"admin": True},
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"
    assert calls["validated"] == ["L-1"]
    assert calls["saved_user"]["location_name"] == "Name-L-1"
    assert calls["marked"] == ["user_profile"]


def test_set_install_profile_applies_capabilities_and_marks_state():
    app, calls = _build_app()
    client = TestClient(app)

    res = client.post(
        "/api/setup/profile/install",
        json={
            "installation_id": "inst-2",
            "os_type": "macos",
            "capabilities": {"web_proxy": True},
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "success"
    assert calls["saved_install"]["capabilities"]["web_proxy"] is True
    assert calls["applied_caps"][0]["web_proxy"] is True
    assert calls["marked"] == ["install_profile"]


def test_profile_getters_and_metrics():
    app, _calls = _build_app()
    client = TestClient(app)

    assert client.get("/api/setup/profiles").status_code == 200
    assert client.get("/api/setup/profile/user").status_code == 200
    assert client.get("/api/setup/profile/install").status_code == 200
    assert client.get("/api/setup/profile/combined").status_code == 200
    assert client.get("/api/setup/installation/metrics").status_code == 200
    assert client.post("/api/setup/installation/moves").status_code == 200


def test_get_user_profile_missing_returns_404():
    def load_user_profile():
        return _result(data=None, locked=False, error=None)

    app, _calls = _build_app(load_user_profile=load_user_profile)
    client = TestClient(app)

    res = client.get("/api/setup/profile/user")
    assert res.status_code == 404
    assert "No user profile found" in res.json()["detail"]
