"""Sonic media console workflow service (Kodi + WantMyMTV)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.services.json_utils import read_json_file, write_json_file
from core.services.template_workspace_service import get_template_workspace_service
from core.services.time_utils import utc_now_iso_z
from wizard.services.launch_adapters import LaunchAdapterExecution
from wizard.services.launch_orchestrator import (
    LaunchIntent,
    get_launch_orchestrator,
)

SUPPORTED_LAUNCHERS = ("kodi", "wantmymtv")


@dataclass(frozen=True)
class _MediaLauncherAdapter:
    action: str
    launcher: str | None

    def starting_state(self, intent: LaunchIntent) -> str:
        return "starting" if self.action == "start" else "stopping"

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        final_state = "ready" if self.action == "start" else "stopped"
        return LaunchAdapterExecution(
            final_state=final_state,
            state_payload={
                "active_launcher": self.launcher if self.action == "start" else None,
                "updated_at": utc_now_iso_z(),
                "last_action": self.action,
            },
        )


class SonicMediaConsoleService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "media-console.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.launch_orchestrator = get_launch_orchestrator(repo_root=self.repo_root)

    def _read_state(self) -> dict[str, Any]:
        return read_json_file(
            self.state_path,
            default={"active_launcher": None, "updated_at": None},
        )

    def _write_state(self, payload: dict[str, Any]) -> None:
        write_json_file(self.state_path, payload, indent=2)

    def _preferred_launcher(self) -> tuple[str, str]:
        try:
            fields = get_template_workspace_service(self.repo_root).read_fields(
                "settings", "sonic"
            )
            workspace_value = str(fields.get("preferred_launcher") or "").strip().lower()
            if workspace_value in SUPPORTED_LAUNCHERS:
                return workspace_value, "template_workspace"
        except Exception:
            pass
        return "kodi", "default"

    def get_status(self) -> dict[str, Any]:
        state = self._read_state()
        preferred_launcher, preferred_source = self._preferred_launcher()
        return {
            "supported_launchers": list(SUPPORTED_LAUNCHERS),
            "active_launcher": state.get("active_launcher"),
            "running": bool(state.get("active_launcher")),
            "preferred_launcher": preferred_launcher,
            "preferred_launcher_source": preferred_source,
            "state_path": str(self.state_path),
            "updated_at": state.get("updated_at"),
            "launch_state_namespace": str(self.repo_root / "memory" / "wizard" / "launch"),
            "session_id": state.get("session_id"),
        }

    def list_launchers(self) -> dict[str, Any]:
        launchers: list[dict[str, Any]] = [
            {
                "id": "kodi",
                "name": "Kodi",
                "description": "10-foot media shell launcher.",
            },
            {
                "id": "wantmymtv",
                "name": "WantMyMTV",
                "description": "Ambient kiosk playback launcher.",
            },
        ]
        preferred_launcher, _ = self._preferred_launcher()
        for launcher in launchers:
            launcher["preferred"] = launcher["id"] == preferred_launcher
        return {
            "count": len(launchers),
            "launchers": launchers,
            "status": self.get_status(),
        }

    def start(self, launcher: str) -> dict[str, Any]:
        normalized = (launcher or "").strip().lower()
        if not normalized:
            normalized, _ = self._preferred_launcher()
        if normalized not in SUPPORTED_LAUNCHERS:
            raise ValueError(f"Unsupported media launcher: {launcher}")
        intent = LaunchIntent(
            target="media-console",
            mode="media",
            launcher=normalized,
            profile_id=normalized,
            auth={"wizard_mode_active": False},
        )
        adapter = _MediaLauncherAdapter(action="start", launcher=normalized)
        payload = self.launch_orchestrator.execute(intent, adapter)["state"]
        self._write_state(payload)
        return payload

    def stop(self) -> dict[str, Any]:
        current_state = self._read_state()
        intent = LaunchIntent(
            target="media-console",
            mode="media",
            launcher=current_state.get("active_launcher"),
            profile_id=current_state.get("active_launcher"),
            auth={"wizard_mode_active": False},
        )
        adapter = _MediaLauncherAdapter(action="stop", launcher=current_state.get("active_launcher"))
        payload = self.launch_orchestrator.execute(intent, adapter)["state"]
        self._write_state(payload)
        return payload


def get_sonic_media_console_service(repo_root: Path | None = None) -> SonicMediaConsoleService:
    return SonicMediaConsoleService(repo_root=repo_root)
