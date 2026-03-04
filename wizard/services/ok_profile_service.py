"""v1.5 logic-assist prompt profile service."""

from __future__ import annotations

from typing import Any

from core.services.template_workspace_service import get_template_workspace_service
from wizard.services.logic_assist_profile import load_logic_assist_profile
from wizard.services.path_utils import get_repo_root


def _instructions_fields() -> dict[str, str]:
    workspace = get_template_workspace_service(get_repo_root())
    return workspace.read_fields("instructions", "logic-assist")


def load_profile() -> dict[str, Any]:
    profile = load_logic_assist_profile()
    instructions = _instructions_fields()
    return {
        "schema_version": profile.schema_version,
        "profile_name": "uDOS v1.5 Logic Assist OK Profile",
        "local_runtime": profile.local_runtime,
        "local_role": profile.local_role,
        "local_model_name": profile.local_model_name,
        "local_context_window": profile.local_context_window,
        "network_primary_provider": profile.network_primary_provider,
        "instructions": instructions,
    }


def render_system_prompt(mode: str = "general") -> str:
    profile = load_logic_assist_profile()
    instructions = _instructions_fields()
    lines = [
        "uDOS v1.5 Logic Assist",
        "You are an advisory-only local assist layer.",
        f"Mode: {mode}",
        f"Local runtime: {profile.local_runtime}",
        f"Role: {profile.local_role}",
        f"Prompt style: {profile.local_prompt_style}",
        "Execution authority belongs to uLogic.",
        "Never claim authority over execution, persistence, or network routing.",
        "Prefer structured Markdown output with explicit next steps and evidence notes.",
    ]

    doctrine = instructions.get("doctrine")
    if doctrine:
        lines.append(f"Doctrine: {doctrine}")
    lines.append(
        f"Execution authority: {instructions.get('execution_authority', 'ulogic')}"
    )
    lines.append(
        f"Network authority: {instructions.get('network_authority', 'wizard_only')}"
    )
    if mode == "coding":
        lines.append("For code assistance, explain reasoning and keep changes auditable.")
    return "\n".join(lines)


def load_template() -> dict[str, Any]:
    profile = load_profile()
    return {
        **profile,
        "quests": [],
        "skills": [],
        "knowledge": [],
    }


def save_profile(payload: dict[str, Any]) -> dict[str, Any]:
    current = load_template()
    current.update(payload or {})
    return current


def add_quest(quest: dict[str, Any]) -> dict[str, Any]:
    profile = load_template()
    profile["quests"] = [*(profile.get("quests") or []), quest]
    return profile


def add_skill(skill: dict[str, Any]) -> dict[str, Any]:
    profile = load_template()
    profile["skills"] = [*(profile.get("skills") or []), skill]
    return profile


def add_knowledge_entry(entry: dict[str, Any]) -> dict[str, Any]:
    profile = load_template()
    profile["knowledge"] = [*(profile.get("knowledge") or []), entry]
    return profile
