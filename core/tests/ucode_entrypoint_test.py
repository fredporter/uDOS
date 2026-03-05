from core.tui.ucode_entry import bootstrap_ucode_keymap_env
from core.tui import ucode_entry as ucode_entry_mod


def test_bootstrap_ucode_keymap_env_mac_defaults():
    env = {"TERM_PROGRAM": "Apple_Terminal", "TERM": "xterm-256color"}
    state = bootstrap_ucode_keymap_env(env=env, tty_env=env)
    assert env["UDOS_KEYMAP_PROFILE"] == "mac-obsidian"
    assert env["UDOS_KEYMAP_SELF_HEAL"] == "1"
    assert env["UDOS_FALLBACK_RAW_EDITOR"] == "1"
    assert state["profile"] == "mac-obsidian"
    assert state["force_fallback"] is False
    assert state["inline_toolbar"] is False


def test_bootstrap_ucode_keymap_env_respects_existing_values():
    env = {
        "UDOS_KEYMAP_PROFILE": "linux-default",
        "UDOS_SMARTPROMPT_FORCE_FALLBACK": "0",
        "UDOS_KEYMAP_SELF_HEAL": "0",
        "UDOS_FALLBACK_RAW_EDITOR": "0",
        "UDOS_MENU_STYLE": "numbered",
        "TERM": "xterm-256color",
        "TERM_PROGRAM": "iTerm.app",
    }
    state = bootstrap_ucode_keymap_env(env=env, tty_env=env)
    assert env["UDOS_KEYMAP_PROFILE"] == "linux-default"
    assert env["UDOS_SMARTPROMPT_FORCE_FALLBACK"] == "0"
    assert env["UDOS_KEYMAP_SELF_HEAL"] == "0"
    assert env["UDOS_FALLBACK_RAW_EDITOR"] == "0"
    assert env["UDOS_MENU_STYLE"] == "numbered"
    assert state["profile"] == "linux-default"


def test_bootstrap_ucode_keymap_env_clears_stale_forced_fallback():
    env = {
        "UDOS_SMARTPROMPT_FORCE_FALLBACK": "1",
        "TERM": "xterm-256color",
        "TERM_PROGRAM": "Apple_Terminal",
    }
    state = bootstrap_ucode_keymap_env(env=env, tty_env=env)
    assert env["UDOS_SMARTPROMPT_FORCE_FALLBACK"] == "0"
    assert state["force_fallback"] is False


def test_bootstrap_ucode_keymap_env_allows_explicit_forced_fallback_opt_in():
    env = {
        "UDOS_SMARTPROMPT_FORCE_FALLBACK": "1",
        "UDOS_SMARTPROMPT_FORCE_FALLBACK_EXPLICIT": "1",
        "TERM": "xterm-256color",
        "TERM_PROGRAM": "Apple_Terminal",
    }
    state = bootstrap_ucode_keymap_env(env=env, tty_env=env)
    assert env["UDOS_SMARTPROMPT_FORCE_FALLBACK"] == "1"
    assert state["force_fallback"] is True


def test_main_execs_bin_udos_tui(monkeypatch, tmp_path):
    module_path = tmp_path / "core" / "tui" / "ucode_entry.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("", encoding="utf-8")
    launcher = tmp_path / "bin" / "udos"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    class _ExecvCalled(Exception):
        def __init__(self, program, argv):
            self.program = program
            self.argv = argv

    monkeypatch.setattr(ucode_entry_mod, "bootstrap_ucode_keymap_env", lambda: {})
    monkeypatch.setattr(ucode_entry_mod, "__file__", str(module_path))
    monkeypatch.setenv("UDOS_ROOT", str(tmp_path))

    def _fake_execv(program, argv):
        raise _ExecvCalled(program, argv)

    monkeypatch.setattr(ucode_entry_mod.os, "execv", _fake_execv)

    try:
        ucode_entry_mod.main(["--", "STATUS"])
    except _ExecvCalled as exc:
        assert exc.program == str(launcher)
        assert exc.argv == [str(launcher), "tui", "--", "STATUS"]
        return
    assert False, "expected execv call"
