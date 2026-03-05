from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.ops_routes as ops_routes_module
import wizard.routes.ucode_routes as ucode_routes_module
import wizard.services.logic_assist_service as logic_assist_service_module
import wizard.services.store as store_module
import wizard.services.task_scheduler as task_scheduler_module
from wizard.routes.ops_routes import create_ops_routes
from wizard.routes.ucode_routes import create_ucode_routes


def test_ucode_and_ops_share_managed_operations_contract(tmp_path, monkeypatch):
    shared_cloud = {
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
    shared_quota = {
        "updated_at": "2026-03-04T00:00:00Z",
        "providers": {
            "openai": {
                "provider": "openai",
                "configured": True,
                "status": "ok",
            }
        },
        "totals": {
            "cost_today": 0.12,
            "cost_this_month": 1.45,
            "requests_today": 3,
            "requests_this_month": 17,
        },
    }

    class _LogicAssist:
        def get_status(self):
            return {
                "local": {
                    "ready": True,
                    "issue": None,
                    "model": "local.gguf",
                    "model_path": "/tmp/local.gguf",
                    "runtime": "gpt4all",
                },
                "context": {"hash": "hash-core", "count": 2},
                "conversations": {"stored": 1},
                "cache": {"entries": 0},
                "network": {
                    **shared_cloud,
                    "budget": {
                        "daily_limit_usd": 10.0,
                        "tier0_daily_limit_usd": 2.0,
                        "tier1_daily_limit_usd": 4.0,
                        "tier2_daily_limit_usd": 4.0,
                        "providers": shared_quota,
                    },
                },
            }

    class _Quota:
        def get_all_quotas(self):
            return shared_quota

    store_module._STORE = None
    monkeypatch.setattr(store_module, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(task_scheduler_module, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(ops_routes_module, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(logic_assist_service_module, "get_logic_assist_service", lambda: _LogicAssist())
    monkeypatch.setattr(
        ucode_routes_module,
        "_get_logic_context_window",
        lambda: 8192,
    )
    monkeypatch.setattr(
        ucode_routes_module,
        "_get_logic_default_model",
        lambda purpose="general": "local.gguf",
    )
    monkeypatch.setattr(
        ucode_routes_module,
        "_get_logic_default_models",
        lambda: {"core": "local.gguf", "dev": "local.gguf"},
    )
    monkeypatch.setattr(ucode_routes_module, "_is_dev_mode_active", lambda: False)
    monkeypatch.setattr(ucode_routes_module, "_logic_auto_fallback_enabled", lambda: True)
    monkeypatch.setattr(
        ucode_routes_module,
        "_write_logic_default_model",
        lambda profile, model: {"profile": profile, "model": model},
    )
    monkeypatch.setattr(ops_routes_module, "get_cloud_execution_plan", lambda: shared_cloud)
    monkeypatch.setattr(ops_routes_module, "get_quota_tracker", lambda: _Quota())

    app = FastAPI()
    app.include_router(create_ucode_routes())
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
    client = TestClient(app)

    logic_res = client.get("/api/ucode/logic/status")
    jobs_res = client.get("/api/ops/planning/jobs")
    config_res = client.get("/api/ops/config/status")

    assert logic_res.status_code == 200
    assert jobs_res.status_code == 200
    assert config_res.status_code == 200

    logic_cloud = logic_res.json()["logic"]["network"]
    jobs_cloud = jobs_res.json()["runtime"]["managed_operations"]["cloud_execution"]
    config_cloud = config_res.json()["managed_operations"]["cloud_execution"]

    for payload in (logic_cloud, jobs_cloud, config_cloud):
        assert payload["blocked_by_quota"] == ["mistral"]
        assert payload["quota_ready_providers"] == ["openai"]
        assert payload["primary"] == "openai"
        assert payload["providers"][0]["quota_allowed"] is False

    assert logic_res.json()["logic"]["network"]["budget"]["providers"]["providers"]["openai"]["status"] == "ok"
    assert jobs_res.json()["runtime"]["managed_operations"]["quota_status"]["providers"]["openai"]["status"] == "ok"
    assert config_res.json()["managed_operations"]["quota_status"]["providers"]["openai"]["status"] == "ok"
