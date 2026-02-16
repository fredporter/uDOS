"""Sonic media console workflow service (Kodi + WantMyMTV)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SUPPORTED_LAUNCHERS = ("kodi", "wantmymtv")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SonicMediaConsoleService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "media-console.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _read_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {"active_launcher": None, "updated_at": None}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"active_launcher": None, "updated_at": None}

    def _write_state(self, payload: Dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        state = self._read_state()
        return {
            "supported_launchers": list(SUPPORTED_LAUNCHERS),
            "active_launcher": state.get("active_launcher"),
            "running": bool(state.get("active_launcher")),
            "state_path": str(self.state_path),
            "updated_at": state.get("updated_at"),
        }

    def list_launchers(self) -> Dict[str, Any]:
        launchers: List[Dict[str, Any]] = [
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
        return {
            "count": len(launchers),
            "launchers": launchers,
            "status": self.get_status(),
        }

    def start(self, launcher: str) -> Dict[str, Any]:
        normalized = (launcher or "").strip().lower()
        if normalized not in SUPPORTED_LAUNCHERS:
            raise ValueError(f"Unsupported media launcher: {launcher}")
        payload = {
            "active_launcher": normalized,
            "updated_at": _utc_now(),
            "last_action": "start",
        }
        self._write_state(payload)
        return payload

    def stop(self) -> Dict[str, Any]:
        payload = {
            "active_launcher": None,
            "updated_at": _utc_now(),
            "last_action": "stop",
        }
        self._write_state(payload)
        return payload


def get_sonic_media_console_service(repo_root: Optional[Path] = None) -> SonicMediaConsoleService:
    return SonicMediaConsoleService(repo_root=repo_root)
