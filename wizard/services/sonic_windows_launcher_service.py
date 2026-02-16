"""Sonic Windows launcher and mode selector service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


VALID_MODES = {"gaming", "media", "install", "wtg"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SonicWindowsLauncherService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.flash_pack_path = (
            self.repo_root / "sonic" / "config" / "flash-packs" / "windows10-entertainment.json"
        )
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "windows-launcher.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _read_flash_pack(self) -> Dict[str, Any]:
        if not self.flash_pack_path.exists():
            return {}
        try:
            return json.loads(self.flash_pack_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _read_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_state(self, payload: Dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        flash_pack = self._read_flash_pack()
        state = self._read_state()
        preferred_shells = ((flash_pack.get("metadata") or {}).get("preferred_shells") or {})

        current_mode = state.get("mode") or "media"
        current_launcher = state.get("launcher") or preferred_shells.get("media") or "kodi"
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
        }

    def set_mode(self, mode: str, launcher: Optional[str] = None, auto_repair: Optional[bool] = None) -> Dict[str, Any]:
        normalized_mode = (mode or "").strip().lower()
        if normalized_mode not in VALID_MODES:
            raise ValueError(f"Unsupported mode: {mode}")

        status = self.get_status()
        payload = {
            "mode": normalized_mode,
            "launcher": launcher or status["launcher"],
            "auto_repair": status["auto_repair"] if auto_repair is None else bool(auto_repair),
            "updated_at": _utc_now(),
            "next_action": "reboot-to-windows",
        }
        self._write_state(payload)
        return payload


def get_sonic_windows_launcher_service(
    repo_root: Optional[Path] = None,
) -> SonicWindowsLauncherService:
    return SonicWindowsLauncherService(repo_root=repo_root)
