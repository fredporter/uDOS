"""Terminal/TTY helpers for interactive detection."""

from __future__ import annotations

import os
import sys
from typing import IO, Mapping, Optional, Tuple


def interactive_tty_status(
    stdin: Optional[IO] = None,
    stdout: Optional[IO] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Tuple[bool, Optional[str]]:
    """Return (interactive, reason) for the current terminal session."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    env = env or os.environ

    try:
        if not hasattr(stdin, "isatty") or not stdin.isatty():
            return False, "stdin is not a TTY"
        if not hasattr(stdout, "isatty") or not stdout.isatty():
            return False, "stdout is not a TTY"
    except Exception as exc:
        return False, f"isatty() check failed: {exc}"

    def _truthy(value: Optional[str]) -> bool:
        if value is None:
            return False
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    term = env.get("TERM", "").lower()
    allow_dumb = _truthy(env.get("UDOS_TTY")) or _truthy(env.get("UDOS_ALLOW_DUMB_TTY"))
    if term in ("", "dumb") and not allow_dumb:
        # Some wrapper terminals report TERM=dumb but still support interactive input.
        wrapper_hints = (
            env.get("TERM_PROGRAM")
            or env.get("COLORTERM")
            or env.get("WT_SESSION")
            or env.get("TMUX")
            or env.get("VSCODE_PID")
        )
        if not wrapper_hints:
            return False, f"TERM={env.get('TERM', '<empty>')}"

    ci = env.get("CI")
    if ci:
        return False, f"CI={ci}"

    return True, None
