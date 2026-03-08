"""Sonic Windows launcher and mode selector service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.services.external_repo_service import resolve_sonic_repo_root
from core.services.json_utils import read_json_file, write_json_file
from core.services.time_utils import utc_now_iso_z
from wizard.services.launch_adapters import LaunchAdapterExecution
from wizard.services.launch_orchestrator import (
    LaunchIntent,
    get_launch_orchestrator,
)

VALID_MODES = {"gaming", "media", "install", "wtg"}


@dataclass(frozen=True)
class _WindowsLauncherAdapter:
    mode: str
    launcher: str
    auto_repair: bool

    def starting_state(self, intent: LaunchIntent) -> str:
        return "starting"

    def execute(self, intent: LaunchIntent) -> LaunchAdapterExecution:
        return LaunchAdapterExecution(
            final_state="ready",
            session_updates={"next_action": "reboot-to-windows"},
            state_payload={
                "mode": self.mode,
                "launcher": self.launcher,
                "auto_repair": self.auto_repair,
                "updated_at": utc_now_iso_z(),
                "next_action": "reboot-to-windows",
            },
        )


class SonicWindowsLauncherService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        sonic_root = resolve_sonic_repo_root(self.repo_root)
        self.flash_pack_path = (
            sonic_root / "config" / "flash-packs" / "windows10-entertainment.json"
        )
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "windows-launcher.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.launch_orchestrator = get_launch_orchestrator(repo_root=self.repo_root)

    def _read_flash_pack(self) -> dict[str, Any]:
        return read_json_file(self.flash_pack_path, default={})

    def _read_state(self) -> dict[str, Any]:
        return read_json_file(self.state_path, default={})

    def _write_state(self, payload: dict[str, Any]) -> None:
        write_json_file(self.state_path, payload, indent=2)

    def get_status(self) -> dict[str, Any]:
        flash_pack = self._read_flash_pack()
        state = self._read_state()
        preferred_shells = ((flash_pack.get("metadata") or {}).get("preferred_shells") or {})

        current_mode = state.get("mode") or "media"
        current_launcher = state.get("launcher") or preferred_shells.get("media") or "kodi"
        session_id = state.get("session_id")
        return {
            "enabled": True,
            "source_flash_pack": str(self.flash_pack_path),
            "state_path": str(self.state_path),
            "available_modes": sorted(VALID_MODES),
            "available_launchers": sorted({value for value in preferred_shells.values() if value} | {"kodi", "wantmymtv", "playnite"}),
            "mode": current_mode,
            "launcher": current_launcher,
            "auto_repair": bool(state.get("auto_repair", True)),
            "boot_target": "windows10-entertainment",
            "updated_at": state.get("updated_at"),
            "launch_state_namespace": str(self.repo_root / "memory" / "wizard" / "launch"),
            "session_id": session_id,
        }

    def set_mode(
        self,
        mode: str,
        launcher: str | None = None,
        auto_repair: bool | None = None,
    ) -> dict[str, Any]:
        normalized_mode = (mode or "").strip().lower()
        if normalized_mode not in VALID_MODES:
            raise ValueError(f"Unsupported mode: {mode}")

        status = self.get_status()
        intent = LaunchIntent(
            target="windows10-entertainment",
            mode=normalized_mode,
            launcher=launcher or status["launcher"],
            profile_id=normalized_mode,
            auth={"wizard_mode_active": False},
        )
        adapter = _WindowsLauncherAdapter(
            mode=normalized_mode,
            launcher=launcher or status["launcher"],
            auto_repair=status["auto_repair"] if auto_repair is None else bool(auto_repair),
        )
        payload = self.launch_orchestrator.execute(intent, adapter)["state"]
        self._write_state(payload)
        return payload


def get_sonic_windows_launcher_service(
    repo_root: Path | None = None,
) -> SonicWindowsLauncherService:
    return SonicWindowsLauncherService(repo_root=repo_root)
