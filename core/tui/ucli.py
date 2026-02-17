"""uCLI single entrypoint with terminal/keymap bootstrap."""

from __future__ import annotations

import os
from typing import Mapping, MutableMapping

from core.tui.ucode import UCLI
from core.utils.tty import detect_terminal_os, interactive_tty_status


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _default_profile_for(os_name: str, term_program: str) -> str:
    if os_name == "mac":
        # Keep Obsidian-aligned profile for iTerm/Terminal/Warp by default.
        return "mac-obsidian"
    if os_name == "windows":
        return "windows-default"
    return "linux-default"


def bootstrap_ucli_keymap_env(
    env: MutableMapping[str, str] | None = None,
    *,
    tty_env: Mapping[str, str] | None = None,
) -> dict:
    """
    Apply startup keymap defaults for consistent single-key navigation in uCLI.

    Explicit user env overrides always win.
    """
    target_env = env if env is not None else os.environ
    source_env = tty_env if tty_env is not None else target_env
    os_name = detect_terminal_os(source_env)
    term_program = (source_env.get("TERM_PROGRAM") or "").strip()
    interactive, reason = interactive_tty_status(env=source_env)

    if not target_env.get("UDOS_KEYMAP_PROFILE"):
        target_env["UDOS_KEYMAP_PROFILE"] = _default_profile_for(os_name, term_program)

    if not target_env.get("UDOS_KEYMAP_SELF_HEAL"):
        target_env["UDOS_KEYMAP_SELF_HEAL"] = "1"

    if not target_env.get("UDOS_FALLBACK_RAW_EDITOR"):
        target_env["UDOS_FALLBACK_RAW_EDITOR"] = "1"

    if not target_env.get("UDOS_MENU_STYLE"):
        target_env["UDOS_MENU_STYLE"] = "hybrid"

    if not target_env.get("UDOS_TUI_CLEAN_STARTUP"):
        target_env["UDOS_TUI_CLEAN_STARTUP"] = "1"

    # Inline toolbar is only useful in fallback mode where prompt_toolkit's
    # bottom toolbar is unavailable.
    if (
        _is_truthy(target_env.get("UDOS_SMARTPROMPT_FORCE_FALLBACK"))
        and not target_env.get("UDOS_PROMPT_TOOLBAR_INLINE")
    ):
        target_env["UDOS_PROMPT_TOOLBAR_INLINE"] = "1"

    return {
        "os": os_name,
        "term_program": term_program or "unknown",
        "interactive": interactive,
        "interactive_reason": reason,
        "profile": target_env.get("UDOS_KEYMAP_PROFILE"),
        "self_heal": _is_truthy(target_env.get("UDOS_KEYMAP_SELF_HEAL")),
        "force_fallback": _is_truthy(target_env.get("UDOS_SMARTPROMPT_FORCE_FALLBACK")),
        "raw_editor": _is_truthy(target_env.get("UDOS_FALLBACK_RAW_EDITOR")),
        "inline_toolbar": _is_truthy(target_env.get("UDOS_PROMPT_TOOLBAR_INLINE")),
    }


def main():
    """Main entry point for uCLI."""
    bootstrap_ucli_keymap_env()
    tui = UCLI()
    tui.run()


if __name__ == "__main__":
    main()
