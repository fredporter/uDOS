"""Terminal/TTY helpers for interactive detection."""

from __future__ import annotations

import os
import platform
import re
import sys
from typing import IO, Dict, Mapping, Optional, Tuple


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


def detect_terminal_os(env: Optional[Mapping[str, str]] = None) -> str:
    """Best-effort terminal OS profile for key mapping."""
    env = env or os.environ
    override = (env.get("UDOS_KEYMAP_OS") or "").strip().lower()
    if override in {"mac", "linux", "windows"}:
        return override

    sysname = platform.system().lower()
    if "darwin" in sysname:
        return "mac"
    if "linux" in sysname:
        return "linux"
    if "windows" in sysname:
        return "windows"
    return "unknown"


def normalize_terminal_input(raw: str) -> str:
    """
    Normalize common literal escape notations into real escape characters.

    Handles patterns such as '^[[B' that may appear when terminals print
    escape sequences literally.
    """
    if not raw:
        return raw
    # Convert caret-notation ESC into actual ESC.
    normalized = raw.replace("^[", "\x1b")
    # Support '\\e' form used by some terminal docs/tools.
    normalized = normalized.replace("\\e", "\x1b")
    return normalized


def strip_ansi_sequences(text: str) -> str:
    """Strip ANSI/CSI/OSC escape sequences from text."""
    if not text:
        return text
    # CSI + single-char escapes + OSC
    csi = r"\x1b\[[0-?]*[ -/]*[@-~]"
    single = r"\x1b[@-Z\\-_]"
    osc = r"\x1b\][^\x07]*(?:\x07|\x1b\\)"
    return re.sub(f"(?:{osc}|{csi}|{single})", "", text)


def strip_literal_escape_sequences(text: str) -> str:
    """
    Strip literal (non-control) escape notations from terminal input.

    Examples removed:
      ^[[A
      ^[[1;2B
      \\x1b[15~
    """
    if not text:
        return text
    literal_caret = r"\^\[\[[0-9;?]*[A-Za-z~]"
    literal_hex = r"\\x1b\[[0-9;?]*[A-Za-z~]"
    return re.sub(f"(?:{literal_caret}|{literal_hex})", "", text)


def _special_key_map(os_profile: str) -> Dict[str, str]:
    base = {
        # Arrow/navigation keys (CSI + SS3 variants)
        "\x1b[A": "UP",
        "\x1b[B": "DOWN",
        "\x1b[C": "RIGHT",
        "\x1b[D": "LEFT",
        "\x1bOA": "UP",
        "\x1bOB": "DOWN",
        "\x1bOC": "RIGHT",
        "\x1bOD": "LEFT",
        "\x1b[H": "HOME",
        "\x1b[F": "END",
        "\x1bOH": "HOME",
        "\x1bOF": "END",
        "\x1b[3~": "DELETE",
        # Function keys
        "\x1bOP": "F1",
        "\x1bOQ": "F2",
        "\x1bOR": "F3",
        "\x1bOS": "F4",
        "\x1b[11~": "F1",
        "\x1b[12~": "F2",
        "\x1b[13~": "F3",
        "\x1b[14~": "F4",
        "\x1b[15~": "F5",
        "\x1b[17~": "F6",
        "\x1b[18~": "F7",
        "\x1b[19~": "F8",
        "\x1b[[A": "F1",
        "\x1b[[B": "F2",
        "\x1b[[C": "F3",
        "\x1b[[D": "F4",
        # Meta-digit aliases
        "\x1b1": "F1",
        "\x1b2": "F2",
        "\x1b3": "F3",
        "\x1b4": "F4",
        "\x1b5": "F5",
        "\x1b6": "F6",
        "\x1b7": "F7",
        "\x1b8": "F8",
    }
    # macOS terminals frequently emit SS3 arrow variants even in normal mode.
    if os_profile == "mac":
        base.update(
            {
                "\x1b[1~": "HOME",
                "\x1b[4~": "END",
            }
        )
    # Linux/xterm navigation variants.
    if os_profile == "linux":
        base.update(
            {
                "\x1b[7~": "HOME",
                "\x1b[8~": "END",
            }
        )
    return base


def parse_special_key(raw: str, env: Optional[Mapping[str, str]] = None) -> Optional[str]:
    """
    Parse a raw terminal token into a normalized special-key name.

    Returns values like: UP, DOWN, LEFT, RIGHT, HOME, END, DELETE, F1..F8.
    """
    if not raw:
        return None
    env = env or os.environ
    os_profile = detect_terminal_os(env)
    normalized = normalize_terminal_input(raw)
    key_name = _special_key_map(os_profile).get(normalized)
    if key_name:
        return key_name

    # Self-heal: when unknown escape appears, try coarse fallback for arrows.
    self_heal = str(env.get("UDOS_KEYMAP_SELF_HEAL", "1")).strip().lower() in {"1", "true", "yes", "on"}
    if self_heal and normalized.startswith("\x1b[") and normalized:
        last = normalized[-1]
        if last == "A":
            return "UP"
        if last == "B":
            return "DOWN"
        if last == "C":
            return "RIGHT"
        if last == "D":
            return "LEFT"
    return None
