"""Wizard server configuration model."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_WIZARD_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "wizard.json"


@dataclass
class WizardConfig:
    """Wizard Server configuration."""

    host: str = "0.0.0.0"
    port: int = 8765
    debug: bool = False

    requests_per_minute: int = 60
    requests_per_hour: int = 1000

    ai_budget_daily: float = 10.0
    ai_budget_monthly: float = 100.0

    plugin_repo_enabled: bool = True
    plugin_auto_update: bool = False

    web_proxy_enabled: bool = True
    ok_gateway_enabled: bool = False

    github_webhook_secret: Optional[str] = None
    github_webhook_secret_key_id: Optional[str] = None
    github_allowed_repo: str = "fredporter/uDOS-dev"
    github_default_branch: str = "main"
    github_push_enabled: bool = False
    admin_api_key_id: Optional[str] = None
    icloud_enabled: bool = False
    oauth_enabled: bool = False
    compost_cleanup_days: int = 30
    compost_cleanup_dry_run: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WizardConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def load(cls, path: Path) -> "WizardConfig":
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    return cls()
                if "ok_gateway_enabled" not in data and "ai_gateway_enabled" in data:
                    data["ok_gateway_enabled"] = data.get("ai_gateway_enabled")
                return cls.from_dict(data)
            except (json.JSONDecodeError, OSError, ValueError):
                return cls()
        return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def resolve_wizard_config_path(path: Optional[Path] = None) -> Path:
    if path is not None:
        return path
    env_path = None
    if "WIZARD_CONFIG_PATH" in os.environ:
        env_path = Path(os.environ["WIZARD_CONFIG_PATH"]).expanduser()
    return env_path or DEFAULT_WIZARD_CONFIG_PATH


def load_wizard_config_data(
    path: Optional[Path] = None,
    defaults: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    config_path = resolve_wizard_config_path(path)
    merged = dict(defaults or {})
    if not config_path.exists():
        return merged
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return merged
        if "ok_gateway_enabled" not in data and "ai_gateway_enabled" in data:
            data["ok_gateway_enabled"] = data.get("ai_gateway_enabled")
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return merged


def save_wizard_config_data(
    config: Dict[str, Any],
    path: Optional[Path] = None,
) -> None:
    config_path = resolve_wizard_config_path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
