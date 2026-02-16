"""Sonic Windows gaming profile automation service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


PROFILE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "performance": {
        "power_plan": "high_performance",
        "launchers": ["steam", "epic", "playnite"],
        "background_services": {"windows_update": "deferred", "indexing": "reduced"},
        "gpu_hint": "max_performance",
    },
    "balanced": {
        "power_plan": "balanced",
        "launchers": ["steam", "playnite"],
        "background_services": {"windows_update": "normal", "indexing": "normal"},
        "gpu_hint": "balanced",
    },
    "streaming": {
        "power_plan": "balanced",
        "launchers": ["steam", "obs", "playnite"],
        "background_services": {"windows_update": "deferred", "indexing": "reduced"},
        "gpu_hint": "encoder_priority",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SonicWindowsGamingProfileService:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.state_dir = self.repo_root / "memory" / "wizard" / "sonic"
        self.state_path = self.state_dir / "windows-gaming-profile.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _read_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {"profile_id": None, "settings": {}, "updated_at": None}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"profile_id": None, "settings": {}, "updated_at": None}

    def _write_state(self, payload: Dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_profiles(self) -> Dict[str, Any]:
        return {
            "count": len(PROFILE_TEMPLATES),
            "profiles": [{"id": key, "settings": value} for key, value in PROFILE_TEMPLATES.items()],
            "active": self._read_state(),
            "state_path": str(self.state_path),
        }

    def apply_profile(self, profile_id: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        key = (profile_id or "").strip().lower()
        if key not in PROFILE_TEMPLATES:
            raise ValueError(f"Unsupported gaming profile: {profile_id}")
        settings = dict(PROFILE_TEMPLATES[key])
        if extra:
            settings.update(extra)
        payload = {
            "profile_id": key,
            "settings": settings,
            "updated_at": _utc_now(),
            "automation_status": "applied",
        }
        self._write_state(payload)
        return payload


def get_sonic_windows_gaming_profile_service(
    repo_root: Optional[Path] = None,
) -> SonicWindowsGamingProfileService:
    return SonicWindowsGamingProfileService(repo_root=repo_root)
