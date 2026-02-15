from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.ucode_dispatch_routes import create_ucode_dispatch_routes


def _build_app(**overrides):
    calls = overrides.setdefault("calls", {})

    def dispatch_core(command, payload, corr_id):
        calls["dispatch_core"] = {"command": command, "corr_id": corr_id}
        return {"result": {"output": "ok"}}

    def dispatch_ok_stream_command(**kwargs):
        return None

    router = create_ucode_dispatch_routes(
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
        dispatch_ok_stream_command=overrides.get(
            "dispatch_ok_stream_command", dispatch_ok_stream_command
        ),
        is_dev_mode_active=overrides.get("is_dev_mode_active", lambda: False),
        resolve_ok_model=overrides.get("resolve_ok_model", lambda model, _purpose: model or "test-model"),
        ok_auto_fallback_enabled=overrides.get("ok_auto_fallback_enabled", lambda: True),
        run_ok_local_stream=overrides.get("run_ok_local_stream", lambda prompt, model: []),
        run_ok_cloud=overrides.get("run_ok_cloud", lambda prompt: ("", "model")),
        ok_cloud_available=overrides.get("ok_cloud_available", lambda: False),
        record_ok_output=overrides.get("record_ok_output", lambda **kwargs: {}),
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/ucode")
    return app, calls


def test_dispatch_requires_dispatcher():
    app, _calls = _build_app(dispatcher=None)
    client = TestClient(app)

    res = client.post("/api/ucode/dispatch", json={"command": "HELP"})
    assert res.status_code == 500
    assert "dispatcher unavailable" in res.json()["detail"].lower()


def test_dispatch_calls_core():
    app, calls = _build_app()
    client = TestClient(app)

    res = client.post("/api/ucode/dispatch", json={"command": " HELP "})
    assert res.status_code == 200
    assert calls["dispatch_core"]["command"] == "HELP"
    assert len(calls["reset_tokens"]) == 1


def test_stream_rejects_empty_command():
    app, _calls = _build_app()
    client = TestClient(app)

    res = client.post("/api/ucode/dispatch/stream", json={"command": "   "})
    assert res.status_code == 400
    assert "command is required" in res.json()["detail"].lower()


def test_stream_emits_chunks_and_result():
    app, _calls = _build_app(
        dispatch_core=lambda command, payload, corr_id: {"result": {"output": "hello world"}}
    )
    client = TestClient(app)

    res = client.post("/api/ucode/dispatch/stream", json={"command": "HELP"})
    assert res.status_code == 200
    body = res.text
    assert "event: start" in body
    assert "event: chunk" in body
    assert "event: result" in body
