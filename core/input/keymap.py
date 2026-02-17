"""Canonical key decoding for uCLI input handling."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional

from core.utils.tty import (
    detect_terminal_os,
    normalize_terminal_input,
    parse_special_key,
    strip_literal_escape_sequences,
)


VALID_KEYMAP_PROFILES = {
    "mac-obsidian",
    "mac-terminal",
    "linux-default",
    "windows-default",
}


@dataclass
class DecodedKey:
    raw: str
    normalized: str
    profile: str
    action: str
    special: Optional[str] = None


def resolve_keymap_profile(env: Optional[Mapping[str, str]] = None) -> str:
    env = env or os.environ
    explicit = (env.get("UDOS_KEYMAP_PROFILE") or "").strip().lower()
    if explicit in VALID_KEYMAP_PROFILES:
        return explicit

    os_profile = detect_terminal_os(env)
    if os_profile == "mac":
        return "mac-obsidian"
    if os_profile == "linux":
        return "linux-default"
    if os_profile == "windows":
        return "windows-default"
    return "linux-default"


def decode_key_input(raw: str, env: Optional[Mapping[str, str]] = None) -> DecodedKey:
    env = env or os.environ
    profile = resolve_keymap_profile(env)
    normalized = normalize_terminal_input(raw or "")
    special = parse_special_key(normalized, env=env)

    if special:
        if special.startswith("F"):
            return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action=f"FKEY_{special[1:]}", special=special)
        nav_map = {
            "UP": "NAV_UP",
            "DOWN": "NAV_DOWN",
            "LEFT": "NAV_LEFT",
            "RIGHT": "NAV_RIGHT",
            "HOME": "NAV_HOME",
            "END": "NAV_END",
            "DELETE": "NAV_DELETE",
        }
        if special in nav_map:
            return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action=nav_map[special], special=special)

    if normalized.count("\x1b") > 1:
        return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="NOISE")

    # Canonical basic controls
    if normalized in {"\r", "\n"}:
        return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="SUBMIT")
    if "\t" in normalized:
        return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="OPEN_COMMAND")
    if normalized in {"\x03", "\x04"}:
        return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="CANCEL")

    # mac-first + Obsidian-aligned terminal shortcuts (best-effort in TTY)
    if profile.startswith("mac"):
        if normalized == "\x10":  # Ctrl+P
            return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="OPEN_COMMAND")
        if normalized == "\x0f":  # Ctrl+O
            return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="OPEN_FILE")
    else:
        if normalized == "\x10":  # Ctrl+P on Linux is commonly used for previous/history
            return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="NAV_UP")

    literal_stripped = strip_literal_escape_sequences(normalized)
    if literal_stripped != normalized and not literal_stripped.strip():
        return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="NOISE")

    return DecodedKey(raw=raw or "", normalized=normalized, profile=profile, action="TEXT")
