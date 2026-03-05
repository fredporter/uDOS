from __future__ import annotations

import json
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

import wizard.routes.ops_routes as ops_routes_module
import wizard.services.logic_assist_service as logic_assist_service_module
import wizard.services.store as store_module
import wizard.services.task_scheduler as task_scheduler_module
from core.services.path_service import clear_repo_root_cache
from wizard.routes.ops_routes import create_ops_routes
from wizard.routes.ucode_routes import create_ucode_routes
from wizard.services.quota_tracker import APIProvider


class DemoQuotaTracker:
    def __init__(self, quota_status: dict[str, Any], blocked: set[APIProvider] | None = None):
        self._quota_status = quota_status
        self._blocked = blocked or set()

    def get_all_quotas(self) -> dict[str, Any]:
        return self._quota_status

    def can_request(self, provider: APIProvider, estimated_tokens: int = 0) -> bool:
        return provider not in self._blocked


class DemoLogicAssist:
    def __init__(self, cloud_status: dict[str, Any], quota_status: dict[str, Any]):
        self._cloud_status = cloud_status
        self._quota_status = quota_status

    def get_status(self) -> dict[str, Any]:
        return {
            "local": {
                "ready": True,
                "issue": None,
                "model": "local.gguf",
                "model_path": "/demo/local.gguf",
                "runtime": "gpt4all",
            },
            "context": {
                "workspace": "core",
                "hash": "demo-context-hash",
                "files": ["AGENTS.md", "core/AGENTS.md"],
                "count": 2,
            },
            "conversations": {"stored": 1},
            "cache": {"entries": 0},
            "network": {
                **self._cloud_status,
                "budget": {
                    "daily_limit_usd": 10.0,
                    "tier0_daily_limit_usd": 2.0,
                    "tier1_daily_limit_usd": 4.0,
                    "tier2_daily_limit_usd": 4.0,
                    "providers": self._quota_status,
                },
            },
        }


def build_cloud_contract(*, blocked_provider: str, primary: str) -> dict[str, Any]:
    providers = ["mistral", "openai", "anthropic"]
    return {
        "ready": True,
        "issue": None,
        "available_providers": ["mistral", "openai"],
        "unavailable_providers": ["anthropic"],
        "quota_ready_providers": [primary],
        "blocked_by_quota": [blocked_provider],
        "primary": primary,
        "estimated_tokens": 24,
        "providers": [
            {
                "provider": "mistral",
                "configured": True,
                "quota_allowed": blocked_provider != "mistral",
            },
            {
                "provider": "openai",
                "configured": True,
                "quota_allowed": blocked_provider != "openai",
            },
            {
                "provider": "anthropic",
                "configured": False,
                "quota_allowed": True,
            },
        ],
    }


def build_quota_status(primary: str) -> dict[str, Any]:
    return {
        "updated_at": "2026-03-04T00:00:00Z",
        "providers": {
            primary: {
                "provider": primary,
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


def ensure_runtime_root(runtime_root: Path) -> Path:
    (runtime_root / "memory" / "wizard").mkdir(parents=True, exist_ok=True)
    (runtime_root / "memory" / "vault").mkdir(parents=True, exist_ok=True)
    return runtime_root


def ensure_dev_demo_root(runtime_root: Path) -> Path:
    ensure_runtime_root(runtime_root)
    (runtime_root / "dev" / "ops" / "workflows").mkdir(parents=True, exist_ok=True)
    (runtime_root / "dev" / "ops" / "scheduler").mkdir(parents=True, exist_ok=True)
    (runtime_root / "dev" / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
    return runtime_root


@contextmanager
def demo_runtime(
    runtime_root: Path,
    *,
    blocked_provider: str = "mistral",
    primary_provider: str = "openai",
) -> Iterator[TestClient]:
    runtime_root = ensure_runtime_root(runtime_root)
    blocked_map = {
        "mistral": {APIProvider.MISTRAL},
        "openai": {APIProvider.OPENAI},
        "anthropic": {APIProvider.ANTHROPIC},
        "gemini": {APIProvider.GEMINI},
        "openrouter": {APIProvider.MISTRAL},
    }
    cloud_status = build_cloud_contract(
        blocked_provider=blocked_provider,
        primary=primary_provider,
    )
    quota_status = build_quota_status(primary_provider)
    quota_tracker = DemoQuotaTracker(quota_status, blocked=blocked_map.get(blocked_provider, set()))

    store_module._STORE = None
    logic_assist_service_module._LOGIC_ASSIST = None
    clear_repo_root_cache()

    with ExitStack() as stack:
        stack.enter_context(patch.object(store_module, "get_repo_root", lambda: runtime_root))
        stack.enter_context(patch.object(task_scheduler_module, "get_repo_root", lambda: runtime_root))
        stack.enter_context(patch.object(ops_routes_module, "get_repo_root", lambda: runtime_root))
        stack.enter_context(
            patch.object(
                logic_assist_service_module,
                "get_logic_assist_service",
                lambda repo_root=None: DemoLogicAssist(cloud_status, quota_status),
            )
        )
        stack.enter_context(patch.object(ops_routes_module, "get_cloud_execution_plan", lambda: cloud_status))
        stack.enter_context(patch.object(ops_routes_module, "get_quota_tracker", lambda: quota_tracker))
        stack.enter_context(patch.object(task_scheduler_module, "get_quota_tracker", lambda: quota_tracker))

        app = FastAPI()
        app.include_router(create_ucode_routes())
        app.include_router(
            create_ops_routes(
                auth_guard=None,
                session_resolver=lambda _request: {
                    "subject": "release-demo",
                    "email": "release@example.com",
                    "display_name": "Release Demo",
                    "role": "admin",
                },
            )
        )
        yield TestClient(app)

    store_module._STORE = None
    logic_assist_service_module._LOGIC_ASSIST = None
    clear_repo_root_cache()


def write_report(output_path: Path, payload: dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
