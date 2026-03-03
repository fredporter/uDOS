"""Markdown-backed v1.5 logic-assist profile contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.services.template_workspace_service import get_template_workspace_service
from wizard.services.path_utils import get_repo_root

_COMPONENT_ID = "logic-assist"


def _to_bool(value: str | bool | None, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _to_int(value: str | int | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _to_float(value: str | float | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class LogicAssistProfile:
    component_id: str
    local_runtime: str
    local_role: str
    local_model_name: str
    local_model_path: str
    local_context_window: int
    local_prompt_style: str
    network_enabled: bool
    network_primary_provider: str
    network_tier0_provider: str
    network_tier1_provider: str
    network_tier2_provider: str
    daily_limit_usd: float
    tier0_daily_limit_usd: float
    tier1_daily_limit_usd: float
    tier2_daily_limit_usd: float
    auto_defer_when_exceeded: bool
    response_cache_enabled: bool
    schema_version: str
    effective_path: str
    effective_source: str
    fields: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_logic_assist_profile(repo_root: Path | None = None) -> LogicAssistProfile:
    root = repo_root or get_repo_root()
    workspace = get_template_workspace_service(root)
    snapshot = workspace.read_document("settings", _COMPONENT_ID)
    fields = workspace.parse_fields(str(snapshot.get("effective_content") or ""))

    return LogicAssistProfile(
        component_id=_COMPONENT_ID,
        local_runtime=fields.get("local_runtime", "gpt4all"),
        local_role=fields.get("local_role", "advisory_only"),
        local_model_name=fields.get(
            "local_model_name", "mistral-7b-instruct-v0.2.Q4_0.gguf"
        ),
        local_model_path=fields.get("local_model_path", "memory/models/gpt4all"),
        local_context_window=_to_int(fields.get("local_context_window"), 8192),
        local_prompt_style=fields.get("local_prompt_style", "markdown_runbook"),
        network_enabled=_to_bool(fields.get("network_enabled"), True),
        network_primary_provider=fields.get("network_primary_provider", "mistral"),
        network_tier0_provider=fields.get("network_tier0_provider", "openrouter"),
        network_tier1_provider=fields.get("network_tier1_provider", "mistral"),
        network_tier2_provider=fields.get("network_tier2_provider", "openai"),
        daily_limit_usd=_to_float(fields.get("daily_limit_usd"), 10.0),
        tier0_daily_limit_usd=_to_float(fields.get("tier0_daily_limit_usd"), 2.0),
        tier1_daily_limit_usd=_to_float(fields.get("tier1_daily_limit_usd"), 4.0),
        tier2_daily_limit_usd=_to_float(fields.get("tier2_daily_limit_usd"), 4.0),
        auto_defer_when_exceeded=_to_bool(
            fields.get("auto_defer_when_exceeded"), True
        ),
        response_cache_enabled=_to_bool(
            fields.get("response_cache_enabled"), True
        ),
        schema_version=fields.get("schema_version", "udos-logic-assist-v1.5"),
        effective_path=str(snapshot.get("effective_path") or ""),
        effective_source=str(snapshot.get("effective_source") or "seeded"),
        fields=fields,
    )


def write_logic_assist_field(
    field_name: str, value: str, repo_root: Path | None = None
) -> dict[str, Any]:
    root = repo_root or get_repo_root()
    workspace = get_template_workspace_service(root)
    return workspace.write_user_field("settings", _COMPONENT_ID, field_name, value)
