from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient

from wizard.routes.ucode_template_routes import create_ucode_template_routes


def _build_app(**overrides):
    calls = overrides.setdefault("calls", {})

    def dispatch_core(command, payload, corr_id):
        calls.setdefault("commands", []).append(command)
        return {
            "status": "ok",
            "command": command,
            "result": {"status": "success", "output": command},
        }

    router = create_ucode_template_routes(
        logger=overrides.get(
            "logger",
            type(
                "L",
                (),
                {"info": lambda *a, **k: None, "warn": lambda *a, **k: None},
            )(),
        ),
        dispatcher=overrides.get("dispatcher", object()),
        new_corr_id=overrides.get("new_corr_id", lambda prefix: "C-1"),
        set_corr_id=overrides.get("set_corr_id", lambda corr_id: {"token": corr_id}),
        reset_corr_id=overrides.get(
            "reset_corr_id", lambda token: calls.setdefault("reset_tokens", []).append(token)
        ),
        dispatch_core=overrides.get("dispatch_core", dispatch_core),
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/ucode")
    return app, calls


def test_template_routes_surface_template_bridge_failures(monkeypatch):
    def _fail(command, payload, corr_id):
        _ = (command, payload, corr_id)
        raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable")

    app, _calls = _build_app(dispatch_core=_fail)
    client = TestClient(app)

    res = client.get("/api/ucode/templates")
    assert res.status_code == 500
    assert "dispatcher unavailable" in res.json()["detail"].lower()


def test_template_routes_dispatch_ucode_template_commands():
    app, calls = _build_app()
    client = TestClient(app)

    list_res = client.get("/api/ucode/templates")
    family_res = client.get("/api/ucode/templates/missions")
    read_res = client.get("/api/ucode/templates/captures/CAPTURE-template")
    dup_res = client.post(
        "/api/ucode/templates/submissions/DEVICE-SUBMISSION-template/duplicate",
        json={"target_name": "my-device-template"},
    )

    assert list_res.status_code == 200
    assert family_res.status_code == 200
    assert read_res.status_code == 200
    assert dup_res.status_code == 200
    assert len(calls["reset_tokens"]) == 4
    assert list_res.json()["command"] == "UCODE TEMPLATE LIST"
    assert family_res.json()["command"] == "UCODE TEMPLATE LIST missions"
    assert read_res.json()["command"] == "UCODE TEMPLATE READ captures CAPTURE-template"
    assert dup_res.json()["command"] == "UCODE TEMPLATE DUPLICATE submissions DEVICE-SUBMISSION-template my-device-template"
