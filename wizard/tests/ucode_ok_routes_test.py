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


def _build_client(ok_history=None, cloud_status=None):
    ok_history = ok_history or []
    cloud_status = cloud_status or {"ready": True, "issue": None}
    app = FastAPI()
    app.include_router(
        create_ucode_ok_routes(
            logger=_Logger(),
            ok_history=ok_history,
            get_ok_local_status=lambda: {
                "ready": True,
                "model": "m1",
                "context_hash": "ctx-123",
                "context_files": 4,
                "conversation_store": 2,
                "cache_entries": 1,
            },
            get_ok_cloud_status=lambda: cloud_status,
            get_ok_context_window=lambda: 8192,
            get_ok_default_model=lambda: "m1",
            ok_auto_fallback_enabled=lambda: True,
            load_ok_modes_config=lambda: {"modes": {"ofvibe": {"models": [{"name": "m1"}], "default_models": {"core": "m1"}}}},
            write_ok_modes_config=lambda _cfg: None,
            run_ok_cloud=lambda prompt: (f"cloud:{prompt}", "m-cloud"),
        )
    )
    return TestClient(app)


def test_ok_status_and_history():
    client = _build_client(ok_history=[{"id": 1}])
    res = client.get("/logic/status")
    assert res.status_code == 200
    assert res.json()["logic"]["default_model"] == "m1"
    assert res.json()["logic"]["context_hash"] == "ctx-123"
    assert res.json()["logic"]["conversation_store"] == 2

    res = client.get("/logic/history")
    assert res.status_code == 200
    assert len(res.json()["history"]) == 1


def test_ok_status_preserves_quota_aware_cloud_contract():
    client = _build_client(
        cloud_status={
            "ready": True,
            "issue": None,
            "available_providers": ["mistral", "openai"],
            "unavailable_providers": ["anthropic"],
            "quota_ready_providers": ["openai"],
            "blocked_by_quota": ["mistral"],
            "primary": "openai",
            "estimated_tokens": 24,
            "providers": [
                {"provider": "mistral", "configured": True, "quota_allowed": False},
                {"provider": "openai", "configured": True, "quota_allowed": True},
            ],
        }
    )

    res = client.get("/logic/status")

    assert res.status_code == 200
    cloud = res.json()["logic"]["cloud"]
    assert cloud["blocked_by_quota"] == ["mistral"]
    assert cloud["quota_ready_providers"] == ["openai"]
    assert cloud["primary"] == "openai"
    assert cloud["providers"][0]["quota_allowed"] is False


def test_ok_model_and_cloud_routes():
    client = _build_client()
    res = client.post("/logic/model", json={"model": "m2", "profile": "core"})
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    res = client.post("/logic/cloud", json={"prompt": "hi"})
    assert res.status_code == 200
    assert res.json()["response"] == "cloud:hi"


def test_ok_cloud_route_requires_ready_status():
    client = _build_client(cloud_status={"ready": False, "issue": "missing"})
    res = client.post("/logic/cloud", json={"prompt": "hi"})
    assert res.status_code == 400
