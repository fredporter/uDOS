from core.input.keymap import decode_key_input, resolve_keymap_profile


def test_resolve_keymap_profile_mac_default():
    profile = resolve_keymap_profile({"UDOS_KEYMAP_OS": "mac"})
    assert profile == "mac-obsidian"


def test_resolve_keymap_profile_override():
    assert resolve_keymap_profile({"UDOS_KEYMAP_PROFILE": "mac-obsidian"}) == "mac-obsidian"
    assert resolve_keymap_profile({"UDOS_KEYMAP_PROFILE": "linux-default"}) == "linux-default"


def test_decode_key_input_function_and_nav():
    env = {"UDOS_KEYMAP_PROFILE": "linux-default", "UDOS_KEYMAP_SELF_HEAL": "1"}
    assert decode_key_input("\x1b[19~", env=env).action == "FKEY_8"
    assert decode_key_input("^[[B", env=env).action == "NAV_DOWN"


def test_decode_key_input_mac_obsidian_shortcuts():
    env = {"UDOS_KEYMAP_PROFILE": "mac-obsidian"}
    assert decode_key_input("\x10", env=env).action == "OPEN_COMMAND"  # Ctrl+P
    assert decode_key_input("\x0f", env=env).action == "OPEN_FILE"  # Ctrl+O


def test_decode_key_input_literal_sequence_prefers_last_nav():
    env = {"UDOS_KEYMAP_PROFILE": "mac-obsidian"}
    assert decode_key_input("^[[A^[[B", env=env).action == "NAV_DOWN"


def test_decode_key_input_embedded_or_batched_nav():
    env = {"UDOS_KEYMAP_PROFILE": "mac-obsidian", "UDOS_KEYMAP_SELF_HEAL": "1"}
    assert decode_key_input("· ▶ ^[[A", env=env).action == "NAV_UP"
    assert decode_key_input("^[[A^[[A", env=env).action == "NAV_UP"
