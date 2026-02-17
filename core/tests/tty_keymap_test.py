from core.utils.tty import (
    detect_terminal_os,
    normalize_terminal_input,
    parse_special_key,
    strip_ansi_sequences,
)


def test_detect_terminal_os_override():
    assert detect_terminal_os({"UDOS_KEYMAP_OS": "mac"}) == "mac"
    assert detect_terminal_os({"UDOS_KEYMAP_OS": "linux"}) == "linux"


def test_normalize_terminal_input_caret_notation():
    assert normalize_terminal_input("^[[B") == "\x1b[B"
    assert normalize_terminal_input("\\e[15~") == "\x1b[15~"


def test_parse_special_key_arrows_and_fkeys():
    env = {"UDOS_KEYMAP_OS": "linux", "UDOS_KEYMAP_SELF_HEAL": "1"}
    assert parse_special_key("\x1b[B", env=env) == "DOWN"
    assert parse_special_key("^[[A", env=env) == "UP"
    assert parse_special_key("\x1bOP", env=env) == "F1"
    assert parse_special_key("\x1b[19~", env=env) == "F8"


def test_parse_special_key_self_heal_unknown_csi():
    env = {"UDOS_KEYMAP_OS": "mac", "UDOS_KEYMAP_SELF_HEAL": "1"}
    assert parse_special_key("\x1b[1;2B", env=env) == "DOWN"


def test_strip_ansi_sequences():
    text = "\x1b[31mhello\x1b[0m world \x1b[B"
    assert strip_ansi_sequences(text) == "hello world "
