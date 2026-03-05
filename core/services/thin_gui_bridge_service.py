"""Gameplay-to-Thin-GUI bridge helpers.

Keeps profile-to-target resolution and launch-intent persistence in one place
for PLAY/THINGUI command surfaces.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from core.services.logging_api import get_repo_root
from core.services.unified_config_loader import get_config

_DEFAULT_PROFILE_TARGETS: dict[str, str] = {
    "hethack": "http://127.0.0.1:7411",
    "nethack": "http://127.0.0.1:7411",
    "elite": "http://127.0.0.1:7412",
    "rpgbbs": "http://127.0.0.1:7413",
    "crawler3d": "http://127.0.0.1:7424",
}

_DEFAULT_PROFILE_TITLES: dict[str, str] = {
    "hethack": "NetHack",
    "nethack": "NetHack",
    "elite": "Elite",
    "rpgbbs": "RPGBBS",
    "crawler3d": "Crawler3D",
}


@dataclass(frozen=True, slots=True)
class ThinGuiLaunchTarget:
    profile_id: str
    target_url: str
    title: str
    label: str
    mode: str
    extension_owner: str


class ThinGuiBridgeService:
    """Resolve toybox gameplay profiles into Thin GUI launch descriptors."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or get_repo_root()
        self.catalog_path = self.repo_root / "core" / "config" / "lens_skin_game_catalog_v1_5.json"
        self.intent_path = self.repo_root / "memory" / "ucode" / "thin_gui_intent.json"

    def load_catalog(self) -> dict:
        if not self.catalog_path.exists():
            return {"profiles": {}}
        try:
            payload = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"profiles": {}}
        if not isinstance(payload, dict):
            return {"profiles": {}}
        return payload

    def resolve_target(self, profile_id: str) -> ThinGuiLaunchTarget:
        normalized = str(profile_id or "hethack").strip().lower() or "hethack"
        catalog = self.load_catalog()
        raw_profiles = catalog.get("profiles", {})
        profile = raw_profiles.get(normalized, {}) if isinstance(raw_profiles, dict) else {}
        if not isinstance(profile, dict):
            profile = {}

        env_key = f"UDOS_THINGUI_TARGET_{normalized.upper().replace('-', '_')}"
        target_url = str(get_config(env_key, "")).strip() or _DEFAULT_PROFILE_TARGETS.get(normalized, "")
        mode = str(profile.get("ui_mode", "tui")).strip() or "tui"
        extension_owner = str(profile.get("extension_owner", "thin-gui")).strip() or "thin-gui"
        title = _DEFAULT_PROFILE_TITLES.get(normalized, normalized.upper())
        label = str(profile.get("container_id", normalized)).strip() or normalized

        return ThinGuiLaunchTarget(
            profile_id=normalized,
            target_url=target_url,
            title=title,
            label=label,
            mode=mode,
            extension_owner=extension_owner,
        )

    def wizard_route(self, launch: ThinGuiLaunchTarget) -> str:
        base_url = str(get_config("WIZARD_BASE_URL", "http://127.0.0.1:8765")).rstrip("/")
        params = [f"title={quote(launch.title)}", f"label={quote(launch.label)}"]
        if launch.target_url:
            params.append(f"target={quote(launch.target_url, safe=':/?&=%')}")
        return f"{base_url}/#thin-gui?{'&'.join(params)}"

    def write_intent(self, launch: ThinGuiLaunchTarget) -> dict:
        self.intent_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "target": launch.target_url,
            "title": launch.title,
            "label": launch.label,
            "profile_id": launch.profile_id,
            "mode": launch.mode,
            "wizard_route": "#thin-gui",
            "extension": "thin-gui",
            "extension_owner": launch.extension_owner,
        }
        self.intent_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload


def get_thin_gui_bridge_service() -> ThinGuiBridgeService:
    return ThinGuiBridgeService()

