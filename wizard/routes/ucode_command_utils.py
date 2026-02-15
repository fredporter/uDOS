"""Command normalization helpers for uCODE routes."""

from __future__ import annotations


def normalize_ok_command(command: str) -> str:
    if command.startswith("?"):
        rest = command[1:].strip()
        return f"OK {rest}".strip()
    return command
