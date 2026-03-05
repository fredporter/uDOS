from __future__ import annotations

from pathlib import Path

import pytest

import wizard.services.logic_assist_service as logic_service
from wizard.services.logic_assist_profile import LogicAssistProfile
from wizard.services.logic_assist_service import LogicAssistRequest, LogicAssistService


class _QuotaTracker:
    def get_all_quotas(self):
        return {}


class _LocalReady:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    def status(self):
        return type(
            "_Status",
            (),
            {
                "to_dict": lambda self: {
                    "ready": True,
                    "issue": None,
                    "model": "local.gguf",
                    "model_path": "/tmp/local.gguf",
                    "context_window": 8192,
                    "runtime": "gpt4all",
                },
                "ready": True,
                "issue": None,
            },
        )()

    def generate(self, prompt: str, system: str = "") -> str:
        self.calls.append({"prompt": prompt, "system": system})
        return "local-response"


class _LocalDown:
    def __init__(self, issue: str = "gpt4all model missing"):
        self.issue = issue

    def status(self):
        issue = self.issue
        return type(
            "_Status",
            (),
            {
                "to_dict": lambda self: {
                    "ready": False,
                    "issue": issue,
                    "model": "local.gguf",
                    "model_path": "/tmp/local.gguf",
                    "context_window": 8192,
                    "runtime": "gpt4all",
                },
                "ready": False,
                "issue": self.issue,
            },
        )()

    def generate(self, prompt: str, system: str = "") -> str:
        raise RuntimeError(self.issue)


def _profile() -> LogicAssistProfile:
    return LogicAssistProfile(
        component_id="logic-assist",
        local_runtime="gpt4all",
        local_role="advisory_only",
        local_model_name="local.gguf",
        local_model_path="memory/models/gpt4all",
        local_context_window=8192,
        local_prompt_style="markdown_runbook",
        network_enabled=True,
        network_primary_provider="mistral",
        network_tier0_provider="openrouter",
        network_tier1_provider="mistral",
        network_tier2_provider="openai",
        daily_limit_usd=10.0,
        tier0_daily_limit_usd=2.0,
        tier1_daily_limit_usd=4.0,
        tier2_daily_limit_usd=4.0,
        auto_defer_when_exceeded=True,
        response_cache_enabled=False,
        schema_version="udos-logic-assist-v1.5",
        effective_path="settings/logic-assist.md",
        effective_source="test",
        fields={},
    )


def _service(monkeypatch, tmp_path: Path) -> LogicAssistService:
    monkeypatch.setattr(logic_service, "load_logic_assist_profile", lambda repo_root=None: _profile())
    monkeypatch.setattr(logic_service, "get_quota_tracker", lambda: _QuotaTracker())
    monkeypatch.setattr(
        logic_service,
        "build_ok_context_payload",
        lambda workspace="core": (
            {
                "workspace": workspace,
                "hash": "hash-core",
                "files": ["AGENTS.md", "core/AGENTS.md"],
                "count": 2,
                "bundle": {
                    "AGENTS.md": "uDOS does NOT use the term AI. Prefer OK Assistant and emit UCODE commands.",
                    "core/AGENTS.md": "Core must use Python stdlib only and must not import from wizard.",
                },
            }
            if workspace == "core"
            else {
                "workspace": workspace,
                "hash": "hash-@dev",
                "files": ["AGENTS.md", "dev/AGENTS.md", "dev/ops/AGENTS.md"],
                "count": 3,
                "bundle": {
                    "AGENTS.md": "uDOS does NOT use the term AI. Prefer OK Assistant and emit UCODE commands.",
                    "dev/AGENTS.md": "ucode remains the standard runtime path and runtime logic belongs in wizard or core.",
                    "dev/ops/AGENTS.md": "Keep contributor planning and completion evidence in dev/ops/tasks.json and DEVLOG.md.",
                },
            }
        ),
    )
    monkeypatch.setattr(
        logic_service,
        "render_system_prompt",
        lambda mode="general": "\n".join(
            [
                "uDOS v1.5 Logic Assist",
                "You are an advisory-only local assist layer.",
                f"Mode: {mode}",
                "Execution authority belongs to uLogic.",
                "Never claim authority over execution, persistence, or network routing.",
                "Prefer structured Markdown output with explicit next steps and evidence notes.",
                *(
                    ["For code assistance, explain reasoning and keep changes auditable."]
                    if mode == "coding"
                    else []
                ),
            ]
        ),
    )
    return LogicAssistService(tmp_path)


@pytest.mark.asyncio
async def test_logic_assist_offline_required_rejects_when_local_runtime_unavailable(monkeypatch, tmp_path):
    service = _service(monkeypatch, tmp_path)
    service.local = _LocalDown("gpt4all model missing")
    monkeypatch.setattr(logic_service, "get_cloud_availability", lambda: {"ready": True})

    result = await service.complete(
        LogicAssistRequest(
            prompt="Explain the current lane",
            workspace="@dev",
            offline_required=True,
        ),
        device_id="device-1",
    )

    assert result.success is False
    assert result.error == "gpt4all model missing"


def test_logic_assist_status_reports_context_and_store_metrics(monkeypatch, tmp_path):
    service = _service(monkeypatch, tmp_path)
    service.local = _LocalReady()

    status = service.get_status()

    assert status["context"]["hash"] == "hash-core"
    assert status["context"]["count"] == 2
    assert status["conversations"]["stored"] == 0
    assert status["cache"]["entries"] == 0


@pytest.mark.asyncio
async def test_logic_assist_persists_conversation_and_reuses_recent_turns(monkeypatch, tmp_path):
    service = _service(monkeypatch, tmp_path)
    local = _LocalReady()
    service.local = local
    conversation_id = "dev-thread"

    first = await service.complete(
        LogicAssistRequest(
            prompt="Summarize the tracked workflow lane",
            workspace="@dev",
            mode="coding",
            conversation_id=conversation_id,
        ),
        device_id="device-1",
    )
    second = await service.complete(
        LogicAssistRequest(
            prompt="What is the next safe step?",
            workspace="@dev",
            mode="coding",
            conversation_id=conversation_id,
        ),
        device_id="device-1",
    )

    assert first.success is True
    assert second.success is True
    assert len(local.calls) == 2
    assert "Context bundle hash: hash-@dev" in local.calls[0]["system"]
    assert "ucode remains the standard runtime path" in local.calls[0]["system"]
    assert "Keep contributor planning and completion evidence" in local.calls[0]["system"]
    assert "Workspace request (@dev):" in local.calls[0]["prompt"]
    assert "Recent conversation:" in local.calls[1]["prompt"]
    assert "Summarize the tracked workflow lane" in local.calls[1]["prompt"]

    conversation_path = tmp_path / "memory" / "wizard" / "logic_conversations" / f"{conversation_id}.json"
    assert conversation_path.exists()
    conversation_text = conversation_path.read_text(encoding="utf-8")
    assert "What is the next safe step?" in conversation_text
    assert "local-response" in conversation_text


@pytest.mark.asyncio
async def test_logic_assist_falls_back_to_network_when_local_generation_fails(monkeypatch, tmp_path):
    service = _service(monkeypatch, tmp_path)

    class _LocalBroken(_LocalReady):
        def generate(self, prompt: str, system: str = "") -> str:
            raise RuntimeError("local runtime crashed")

    service.local = _LocalBroken()
    monkeypatch.setattr(
        logic_service,
        "get_cloud_availability",
        lambda: {"ready": True, "available_providers": ["mistral"]},
    )
    monkeypatch.setattr(
        logic_service,
        "run_cloud_with_fallback",
        lambda prompt: ("network-response", "mistral-small"),
    )

    result = await service.complete(
        LogicAssistRequest(
            prompt="Plan the next @dev task",
            workspace="@dev",
            allow_network=True,
        ),
        device_id="device-1",
    )

    assert result.success is True
    assert result.content == "network-response"
    assert result.route["source"] == "network-fallback"
    assert result.route["fallback_reason"] == "local runtime crashed"


@pytest.mark.asyncio
async def test_logic_assist_core_prompt_includes_governance_excerpt(monkeypatch, tmp_path):
    service = _service(monkeypatch, tmp_path)
    local = _LocalReady()
    service.local = local

    result = await service.complete(
        LogicAssistRequest(
            prompt="Explain how to extend the core lane safely",
            workspace="core",
            mode="general",
        ),
        device_id="device-1",
    )

    assert result.success is True
    assert "uDOS does NOT use the term AI" in local.calls[0]["system"]
    assert "Core must use Python stdlib only" in local.calls[0]["system"]
    assert "Execution authority belongs to uLogic." in local.calls[0]["system"]


@pytest.mark.asyncio
async def test_logic_assist_dev_prompt_includes_workspace_rules(monkeypatch, tmp_path):
    service = _service(monkeypatch, tmp_path)
    local = _LocalReady()
    service.local = local

    result = await service.complete(
        LogicAssistRequest(
            prompt="Plan the next contributor task in @dev",
            workspace="@dev",
            mode="coding",
        ),
        device_id="device-1",
    )

    assert result.success is True
    assert "ucode remains the standard runtime path" in local.calls[0]["system"]
    assert "Keep contributor planning and completion evidence in dev/ops/tasks.json" in local.calls[0]["system"]
    assert "For code assistance, explain reasoning and keep changes auditable." in local.calls[0]["system"]
