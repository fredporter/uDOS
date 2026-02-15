"""
Script execution policy helpers for markdown runtime files.

Default behavior is mobile-safe: stdlib ucode command lines are blocked inside
script fences unless explicitly enabled in frontmatter.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_FENCE_TYPES = {"script", "ucode", "cmd", "command", "commands"}

# Core + compatibility command tokens that should be explicit in scripts.
UCODE_COMMAND_TOKENS = {
    "ANCHOR",
    "BACKUP",
    "BAG",
    "BINDER",
    "CLEAN",
    "COMPOST",
    "CONFIG",
    "DATASET",
    "DESTROY",
    "DEV",
    "DRAW",
    "EDIT",
    "EMPIRE",
    "FILE",
    "FIND",
    "GOTO",
    "GRAB",
    "GRID",
    "HEALTH",
    "HELP",
    "HOTKEY",
    "INSTALL",
    "INTEGRATION",
    "LOAD",
    "LOCATION",
    "LOGS",
    "MAINTENANCE",
    "MAP",
    "MIGRATE",
    "MUSIC",
    "NEW",
    "NPC",
    "OK",
    "PANEL",
    "PLACE",
    "PATTERN",
    "PROVIDER",
    "REBOOT",
    "REPAIR",
    "RESTORE",
    "REPLY",
    "READ",
    "RUN",
    "SAVE",
    "SCHEDULER",
    "SCRIPT",
    "SEED",
    "SETUP",
    "SONIC",
    "SPAWN",
    "STORY",
    "SEND",
    "TAG",
    "TALK",
    "TELL",
    "TIDY",
    "TOKEN",
    "UID",
    "UNDO",
    "USER",
    "VERIFY",
    "VIEWPORT",
    "WIZARD",
    "GHOST",
    "WORKSPACE",
}


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _extract_script_fence_commands(content: str) -> List[Tuple[int, str, str]]:
    findings: List[Tuple[int, str, str]] = []
    lines = content.splitlines()
    in_script_fence = False

    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            fence_type = stripped[3:].strip().lower()
            if in_script_fence:
                in_script_fence = False
            else:
                in_script_fence = fence_type in SCRIPT_FENCE_TYPES
            continue

        if not in_script_fence:
            continue
        if not stripped:
            continue
        if stripped.startswith(("#", "//", ";")):
            continue

        token = stripped.split()[0].upper()
        if token in UCODE_COMMAND_TOKENS:
            findings.append((idx, token, stripped))

    return findings


def _extract_frontmatter_flag(content: str, key: str) -> Any:
    lines = content.splitlines()
    if not lines:
        return None
    if lines[0].strip() != "---":
        return None

    for raw in lines[1:]:
        line = raw.strip()
        if line == "---":
            break
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        if k.strip() != key:
            continue
        value = v.strip().strip('"').strip("'")
        return value
    return None


def check_markdown_stdlib_policy(markdown_path: Path) -> Optional[Dict[str, Any]]:
    """
    Enforce mobile-safe script defaults for markdown runtime files.

    Returns None when policy passes, otherwise returns an error payload.
    """
    if markdown_path.suffix.lower() not in {".md", ".markdown"}:
        return None
    if not markdown_path.exists():
        return None

    content = markdown_path.read_text(encoding="utf-8")
    allow_stdlib = _truthy(_extract_frontmatter_flag(content, "allow_stdlib_commands"))
    if allow_stdlib:
        return None

    findings = _extract_script_fence_commands(content)
    if not findings:
        return None

    rendered = ", ".join(f"{token} (line {line_no})" for line_no, token, _ in findings[:5])
    return {
        "status": "error",
        "message": "Script blocked: stdlib ucode commands require explicit opt-in",
        "details": (
            f"Detected command lines in script blocks: {rendered}. "
            "Add `allow_stdlib_commands: true` to markdown frontmatter to enable."
        ),
    }
