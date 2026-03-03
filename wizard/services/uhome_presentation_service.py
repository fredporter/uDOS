"""uHOME presentation workflow service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.services.json_utils import read_json_file, write_json_file
from core.services.template_workspace_service import get_template_workspace_service
from core.services.time_utils import utc_now_iso_z
from wizard.services.launch_adapters import LaunchAdapterExecution
from wizard.services.launch_orchestrator import LaunchIntent, get_launch_orchestrator

SUPPORTED_PRESENTATIONS = ("thin-gui", "steam-console")
SUPPORTED_NODE_ROLES = ("server", "tv-node")


@dataclass(frozen=True)
class _UHomePresentationAdapter:
    action: str
    presentation_mode: str | None
    node_role: str

    def starting_state(self, intent: LaunchIntent) -> str:
        return "starting" if self.action == "start" else "stopping"

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        final_state = "ready" if self.action == "start" else "stopped"
        return LaunchAdapterExecution(
            final_state=final_state,
            state_payload={
                "active_presentation": self.presentation_mode if self.action == "start" else None,
                "node_role": self.node_role,
                "updated_at": utc_now_iso_z(),
                "last_action": self.action,
            },
        )


class UHomePresentationService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.state_dir = self.repo_root / "memory" / "wizard" / "uhome"
        self.state_path = self.state_dir / "presentation.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.launch_orchestrator = get_launch_orchestrator(repo_root=self.repo_root)

    def _read_state(self) -> dict[str, Any]:
        return read_json_file(
            self.state_path,
            default={"active_presentation": None, "updated_at": None, "node_role": "server"},
        )

    def _write_state(self, payload: dict[str, Any]) -> None:
        write_json_file(self.state_path, payload, indent=2)

    def _workspace_fields(self) -> dict[str, str]:
        try:
            return get_template_workspace_service(self.repo_root).read_fields(
                "settings", "uhome"
            )
        except Exception:
            return {}

    def _preferred_presentation(self) -> tuple[str, str]:
        fields = self._workspace_fields()
        workspace_value = str(fields.get("presentation_mode") or "").strip().lower()
        if workspace_value in SUPPORTED_PRESENTATIONS:
            return workspace_value, "template_workspace"
        if workspace_value:
            return SUPPORTED_PRESENTATIONS[0], "template_workspace_invalid"
        return SUPPORTED_PRESENTATIONS[0], "default"

    def _node_role(self) -> tuple[str, str]:
        fields = self._workspace_fields()
        workspace_value = str(fields.get("node_role") or "").strip().lower().replace("_", "-")
        if workspace_value in SUPPORTED_NODE_ROLES:
            return workspace_value, "template_workspace"
        if workspace_value:
            return SUPPORTED_NODE_ROLES[0], "template_workspace_invalid"
        return SUPPORTED_NODE_ROLES[0], "default"

    def get_status(self) -> dict[str, Any]:
        state = self._read_state()
        preferred_presentation, preferred_presentation_source = self._preferred_presentation()
        node_role, node_role_source = self._node_role()
        return {
            "supported_presentations": list(SUPPORTED_PRESENTATIONS),
            "supported_node_roles": list(SUPPORTED_NODE_ROLES),
            "active_presentation": state.get("active_presentation"),
            "running": bool(state.get("active_presentation")),
            "preferred_presentation": preferred_presentation,
            "preferred_presentation_source": preferred_presentation_source,
            "node_role": node_role,
            "node_role_source": node_role_source,
            "state_path": str(self.state_path),
            "updated_at": state.get("updated_at"),
            "launch_state_namespace": str(self.repo_root / "memory" / "wizard" / "launch"),
            "session_id": state.get("session_id"),
        }

    def start(self, presentation: str) -> dict[str, Any]:
        normalized = (presentation or "").strip().lower()
        if not normalized:
            normalized, _ = self._preferred_presentation()
        if normalized not in SUPPORTED_PRESENTATIONS:
            raise ValueError(f"Unsupported uHOME presentation: {presentation}")
        node_role, _ = self._node_role()
        intent = LaunchIntent(
            target="uhome-console",
            mode="home",
            launcher=normalized,
            workspace="uhome",
            profile_id=node_role,
            auth={"wizard_mode_active": False, "uhome_role": node_role},
        )
        adapter = _UHomePresentationAdapter(
            action="start",
            presentation_mode=normalized,
            node_role=node_role,
        )
        payload = self.launch_orchestrator.execute(intent, adapter)["state"]
        self._write_state(payload)
        return payload

    def stop(self) -> dict[str, Any]:
        current_state = self._read_state()
        node_role, _ = self._node_role()
        intent = LaunchIntent(
            target="uhome-console",
            mode="home",
            launcher=current_state.get("active_presentation"),
            workspace="uhome",
            profile_id=node_role,
            auth={"wizard_mode_active": False, "uhome_role": node_role},
        )
        adapter = _UHomePresentationAdapter(
            action="stop",
            presentation_mode=current_state.get("active_presentation"),
            node_role=node_role,
        )
        payload = self.launch_orchestrator.execute(intent, adapter)["state"]
        self._write_state(payload)
        return payload


def get_uhome_presentation_service(
    repo_root: Path | None = None,
) -> UHomePresentationService:
    return UHomePresentationService(repo_root=repo_root)
