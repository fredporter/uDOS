from fastapi import FastAPI
from fastapi.testclient import TestClient

from wizard.routes.ucode_ok_routes import create_ucode_ok_routes


class _Logger:
    def debug(self, *_args, **_kwargs):
        return None

    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None


def _build_client(ok_history=None, cloud_ready=True):
    ok_history = ok_history or []
    app = FastAPI()
    app.include_router(
        create_ucode_ok_routes(
            logger=_Logger(),
            ok_history=ok_history,
            get_ok_local_status=lambda: {"ready": True, "model": "m1"},
            get_ok_cloud_status=lambda: {"ready": cloud_ready, "issue": None if cloud_ready else "missing"},
            get_ok_context_window=lambda: 8192,
            get_ok_default_model=lambda: "m1",
            ok_auto_fallback_enabled=lambda: True,
            load_ai_modes_config=lambda: {"modes": {"ofvibe": {"models": [{"name": "m1"}], "default_models": {"core": "m1"}}}},
            write_ok_modes_config=lambda _cfg: None,
            run_ok_cloud=lambda prompt: (f"cloud:{prompt}", "m-cloud"),
        )
    )
    return TestClient(app)


def test_ok_status_and_history():
    client = _build_client(ok_history=[{"id": 1}])
    res = client.get("/ok/status")
    assert res.status_code == 200
    assert res.json()["ok"]["default_model"] == "m1"

    res = client.get("/ok/history")
    assert res.status_code == 200
    assert len(res.json()["history"]) == 1


def test_ok_model_and_cloud_routes():
    client = _build_client()
    res = client.post("/ok/model", json={"model": "m2", "profile": "core"})
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    res = client.post("/ok/cloud", json={"prompt": "hi"})
    assert res.status_code == 200
    assert res.json()["response"] == "cloud:hi"


def test_ok_cloud_route_requires_ready_status():
    client = _build_client(cloud_ready=False)
    res = client.post("/ok/cloud", json={"prompt": "hi"})
    assert res.status_code == 400
