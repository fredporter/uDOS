from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.services.template_workspace_service import get_template_workspace_service
from wizard.services.path_utils import get_repo_root

_COMPONENT_ID = "ops-control-plane"

_DEFAULT_CAPABILITIES: dict[str, list[str]] = {
    "guest": [],
    "operator": [
        "view_planning",
        "view_automation",
        "retry_queue",
        "manage_alerts",
        "manage_workflows",
        "create_jobs",
    ],
    "admin": [
        "view_planning",
        "view_automation",
        "retry_queue",
        "manage_alerts",
        "manage_workflows",
        "create_jobs",
        "manage_settings",
        "view_system",
        "view_logs",
        "view_config",
        "view_releases",
    ],
}

_CAPABILITY_LABELS: dict[str, str] = {
    "view_planning": "Planning visibility",
    "view_automation": "Automation visibility",
    "retry_queue": "Retry deferred queue work",
    "manage_alerts": "Acknowledge and resolve alerts",
    "manage_workflows": "Approve and escalate workflows",
    "create_jobs": "Create and import jobs",
    "manage_settings": "Change scheduler and control settings",
    "view_system": "See system mode",
    "view_logs": "Browse logs",
    "view_config": "Inspect managed config status",
    "view_releases": "Inspect release surface",
}


@dataclass(frozen=True)
class OpsRoleContract:
    role_names: dict[str, str]
    capabilities: dict[str, list[str]]
    permission_grid: list[dict[str, Any]]
    source: dict[str, Any]

    def for_role(self, role: str) -> dict[str, Any]:
        normalized = (role or "guest").strip().lower() or "guest"
        return {
            "role": normalized,
            "role_name": self.role_names.get(normalized, normalized.title()),
            "capabilities": self.capabilities.get(normalized, []),
            "permission_grid": self.permission_grid,
            "source": self.source,
        }


def _parse_permission_grid(content: str) -> list[dict[str, Any]]:
    lines = [line.rstrip() for line in (content or "").splitlines() if line.strip()]
    table_lines = [line for line in lines if line.lstrip().startswith("|")]
    if len(table_lines) < 3:
        return _default_permission_grid()
    header = [cell.strip().lower().replace(" ", "_") for cell in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, Any]] = []
    for line in table_lines[2:]:
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != len(header):
            continue
        row = dict(zip(header, values))
        capability = str(row.get("capability") or "").strip()
        if not capability:
            continue
        rows.append(
            {
                "capability": capability,
                "label": str(row.get("label") or _CAPABILITY_LABELS.get(capability, capability.replace("_", " "))).strip(),
                "guest": str(row.get("guest") or "deny").strip().lower() in {"allow", "yes", "true", "1"},
                "operator": str(row.get("operator") or "deny").strip().lower() in {"allow", "yes", "true", "1"},
                "admin": str(row.get("admin") or "deny").strip().lower() in {"allow", "yes", "true", "1"},
                "section": str(row.get("section") or "").strip(),
            }
        )
    return rows or _default_permission_grid()


def _default_permission_grid() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for capability in {
        capability_name
        for values in _DEFAULT_CAPABILITIES.values()
        for capability_name in values
    }:
        rows.append(
            {
                "capability": capability,
                "label": _CAPABILITY_LABELS.get(capability, capability.replace("_", " ")),
                "guest": capability in _DEFAULT_CAPABILITIES["guest"],
                "operator": capability in _DEFAULT_CAPABILITIES["operator"],
                "admin": capability in _DEFAULT_CAPABILITIES["admin"],
                "section": "",
            }
        )
    rows.sort(key=lambda item: str(item["label"]))
    return rows


def _capabilities_from_grid(grid: list[dict[str, Any]]) -> dict[str, list[str]]:
    role_caps: dict[str, list[str]] = {"guest": [], "operator": [], "admin": []}
    for row in grid:
        capability = str(row.get("capability") or "").strip()
        if not capability:
            continue
        for role in ("guest", "operator", "admin"):
            if bool(row.get(role)):
                role_caps[role].append(capability)
    return {role: sorted(set(values)) for role, values in role_caps.items()}


def load_ops_role_contract(repo_root: Path | None = None) -> OpsRoleContract:
    root = repo_root or get_repo_root()
    workspace = get_template_workspace_service(root)
    settings_snapshot = workspace.read_document("settings", _COMPONENT_ID)
    instructions_snapshot = workspace.read_document("instructions", _COMPONENT_ID)
    settings_fields = workspace.parse_fields(str(settings_snapshot.get("effective_content") or ""))
    grid = _parse_permission_grid(str(instructions_snapshot.get("effective_content") or ""))
    capabilities = _capabilities_from_grid(grid)
    role_names = {
        "guest": settings_fields.get("guest_role_name", "Observer"),
        "operator": settings_fields.get("operator_role_name", "Operator"),
        "admin": settings_fields.get("admin_role_name", "Administrator"),
    }
    return OpsRoleContract(
        role_names=role_names,
        capabilities=capabilities,
        permission_grid=grid,
        source={
            "settings": settings_snapshot,
            "instructions": instructions_snapshot,
        },
    )
