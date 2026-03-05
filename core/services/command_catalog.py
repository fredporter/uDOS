"""Shared uCODE command catalog and normalization helpers.

Keeps command names and alias parsing in one place to avoid dispatcher drift.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Collection
from typing import Final

CANONICAL_UCODE_COMMANDS: Final[frozenset[str]] = frozenset(
    {
        # Navigation
        "MAP",
        "ANCHOR",
        "GRID",
        "PANEL",
        "GOTO",
        "FIND",
        # Information
        "TELL",
        "HELP",
        "STATUS",
        # Game state
        "BAG",
        "GRAB",
        "SPAWN",
        "SAVE",
        "LOAD",
        # System/runtime
        "HEALTH",
        "VERIFY",
        "REPAIR",
        "REBOOT",
        "SETUP",
        "UID",
        "TOKEN",
        "GHOST",
        "SONIC",
        "MUSIC",
        "DEV",
        "LOGS",
        "SCHEDULER",
        "SCRIPT",
        "THEME",
        "MODE",
        "SKIN",
        "THINGUI",
        "VIEWPORT",
        "DRAW",
        # User/gameplay
        "USER",
        "PLAY",
        "RULE",
        # Maintenance/data
        "DESTROY",
        "UNDO",
        "MIGRATE",
        "SEED",
        "BACKUP",
        "RESTORE",
        "TIDY",
        "CLEAN",
        "COMPOST",
        # NPC/dialogue
        "NPC",
        "SEND",
        # Wizard/config
        "CONFIG",
        "WIZARD",
        "EMPIRE",
        # Workspace/content/files
        "BINDER",
        "PLACE",
        "WORKFLOW",
        "STORY",
        "RUN",
        "READ",
        "FILE",
        # Library/offline assistant
        "LIBRARY",
        "UCODE",
        "OPERATOR",
    }
)

# Legacy/short aliases routed to canonical commands.
SUBCOMMAND_ALIASES: Final[dict[str, str]] = {
    "PAT": "DRAW",
    "PATTERN": "DRAW",
    "DATA": "RUN",
    "STAT": "STATUS",
    "STATE": "STATUS",
    "SEARCH": "FIND",
    "EDIT": "FILE",
    "NEW": "FILE",
    "UCLI": "UCODE",
    "RESTART": "REBOOT",
    "SCHEDULE": "SCHEDULER",
    "TALK": "SEND",
}

# Prefix params injected when aliasing so downstream handlers keep intent.
ALIAS_PREFIX_PARAMS: Final[dict[str, tuple[str, ...]]] = {
    "NEW": ("NEW",),
    "EDIT": ("EDIT",),
}


def normalize_command_tokens(command_text: str) -> tuple[str, list[str]]:
    """Normalize command token and params using canonical alias rules."""
    parts = command_text.strip().split()
    if not parts:
        return "", []

    raw_name = parts[0].upper()
    params = parts[1:]

    cmd_name = SUBCOMMAND_ALIASES.get(raw_name, raw_name)
    if prefix := ALIAS_PREFIX_PARAMS.get(raw_name):
        params = [*prefix, *params]

    return cmd_name, params


@dataclass(slots=True, frozen=True)
class ParsedSlashCommand:
    """Parsed slash-command envelope shared across trust boundaries."""

    body: str
    first_token: str
    rest: str

    @property
    def normalized_ucode_command(self) -> str:
        return f"{self.first_token} {self.rest}".strip()


def parse_slash_command(command_text: str) -> ParsedSlashCommand | None:
    """Parse slash-prefixed command input into normalized token components."""
    if not command_text.startswith("/"):
        return None

    body = command_text[1:].strip()
    if not body:
        return ParsedSlashCommand(body="", first_token="", rest="")

    parts = body.split(None, 1)
    first_token = parts[0].upper()
    rest = parts[1] if len(parts) > 1 else ""
    return ParsedSlashCommand(body=body, first_token=first_token, rest=rest)


def resolve_allowlisted_slash_command(
    parsed: ParsedSlashCommand,
    allowlist: Collection[str],
) -> str | None:
    """Resolve slash command to canonical dispatcher input when allowlisted."""
    normalized_allowlist = {item.strip().upper() for item in allowlist if item.strip()}
    if parsed.first_token in normalized_allowlist:
        return parsed.normalized_ucode_command
    return None
