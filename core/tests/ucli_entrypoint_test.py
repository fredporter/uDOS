from core.tui.ucli import bootstrap_ucli_keymap_env


def test_bootstrap_ucli_keymap_env_mac_defaults():
    env = {"TERM_PROGRAM": "Apple_Terminal", "TERM": "xterm-256color"}
    state = bootstrap_ucli_keymap_env(env=env, tty_env=env)
    assert env["UDOS_KEYMAP_PROFILE"] == "mac-obsidian"
    assert env["UDOS_KEYMAP_SELF_HEAL"] == "1"
    assert env["UDOS_FALLBACK_RAW_EDITOR"] == "1"
    assert state["profile"] == "mac-obsidian"
    assert state["force_fallback"] is False
    assert state["inline_toolbar"] is False


def test_bootstrap_ucli_keymap_env_respects_existing_values():
    env = {
        "UDOS_KEYMAP_PROFILE": "linux-default",
        "UDOS_SMARTPROMPT_FORCE_FALLBACK": "0",
        "UDOS_KEYMAP_SELF_HEAL": "0",
        "UDOS_FALLBACK_RAW_EDITOR": "0",
        "UDOS_MENU_STYLE": "numbered",
        "TERM": "xterm-256color",
        "TERM_PROGRAM": "iTerm.app",
    }
    state = bootstrap_ucli_keymap_env(env=env, tty_env=env)
    assert env["UDOS_KEYMAP_PROFILE"] == "linux-default"
    assert env["UDOS_SMARTPROMPT_FORCE_FALLBACK"] == "0"
    assert env["UDOS_KEYMAP_SELF_HEAL"] == "0"
    assert env["UDOS_FALLBACK_RAW_EDITOR"] == "0"
    assert env["UDOS_MENU_STYLE"] == "numbered"
    assert state["profile"] == "linux-default"
