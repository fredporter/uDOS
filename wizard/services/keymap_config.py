"""Shared keymap configuration helpers for Wizard APIs and web UI."""

from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional

from core.input.keymap import VALID_KEYMAP_PROFILES, resolve_keymap_profile
from core.utils.tty import detect_terminal_os

VALID_OS_OVERRIDES = {"auto", "mac", "linux", "windows"}


def truthy(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def resolve_effective_keymap_state(
    config: Optional[Mapping[str, Any]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    config = dict(config or {})
    effective_env = dict(env or {})

    configured_profile = str(config.get("ucode_keymap_profile") or "").strip().lower()
    configured_os = str(config.get("ucode_keymap_os") or "").strip().lower()
    configured_self_heal = config.get("ucode_keymap_self_heal")
    if not isinstance(configured_self_heal, bool):
        configured_self_heal = truthy(configured_self_heal, default=True)

    if "UDOS_KEYMAP_PROFILE" not in effective_env and configured_profile in VALID_KEYMAP_PROFILES:
        effective_env["UDOS_KEYMAP_PROFILE"] = configured_profile
    if "UDOS_KEYMAP_SELF_HEAL" not in effective_env:
        effective_env["UDOS_KEYMAP_SELF_HEAL"] = "1" if configured_self_heal else "0"
    if "UDOS_KEYMAP_OS" not in effective_env and configured_os in {"mac", "linux", "windows"}:
        effective_env["UDOS_KEYMAP_OS"] = configured_os

    os_override = str(effective_env.get("UDOS_KEYMAP_OS") or "").strip().lower()
    return {
        "active_profile": resolve_keymap_profile(env=effective_env),
        "configured_profile": configured_profile if configured_profile in VALID_KEYMAP_PROFILES else None,
        "self_heal": truthy(effective_env.get("UDOS_KEYMAP_SELF_HEAL"), default=True),
        "configured_self_heal": configured_self_heal,
        "detected_os": detect_terminal_os(env=effective_env),
        "os_override": os_override if os_override in {"mac", "linux", "windows"} else "auto",
        "available_profiles": sorted(VALID_KEYMAP_PROFILES),
        "available_os_overrides": sorted(VALID_OS_OVERRIDES, key=lambda item: (item != "auto", item)),
    }


def apply_keymap_update(
    config: Dict[str, Any],
    env: MutableMapping[str, str],
    profile: Optional[str] = None,
    self_heal: Optional[bool] = None,
    os_override: Optional[str] = None,
) -> None:
    if profile is not None:
        profile = str(profile).strip().lower()
        if profile not in VALID_KEYMAP_PROFILES:
            raise ValueError(f"invalid profile '{profile}'")
        config["ucode_keymap_profile"] = profile
        env["UDOS_KEYMAP_PROFILE"] = profile

    if self_heal is not None:
        config["ucode_keymap_self_heal"] = bool(self_heal)
        env["UDOS_KEYMAP_SELF_HEAL"] = "1" if self_heal else "0"

    if os_override is not None:
        os_override = str(os_override).strip().lower()
        if os_override not in VALID_OS_OVERRIDES:
            raise ValueError(f"invalid os_override '{os_override}'")
        if os_override == "auto":
            config.pop("ucode_keymap_os", None)
            env.pop("UDOS_KEYMAP_OS", None)
        else:
            config["ucode_keymap_os"] = os_override
            env["UDOS_KEYMAP_OS"] = os_override
