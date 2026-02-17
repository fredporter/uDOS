import builtins

from core.input.smart_prompt import SmartPrompt


def test_fallback_ignores_grouped_escape_noise(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    inputs = iter(["^[[A^[[B^[[C^[[D", "OK STATUS"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    result = prompt.ask("▶ ")
    assert result == "OK STATUS"


def test_fallback_ignores_prefixed_literal_escape_noise(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    inputs = iter(["· ▶ ^[[A^[[B^[[C^[[D", "STATUS"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    result = prompt.ask("▶ ")
    assert result == "STATUS"


def test_fallback_renders_toolbar_lines(monkeypatch, capsys):
    prompt = SmartPrompt(use_fallback=True)
    prompt.set_bottom_toolbar_provider(lambda _text: ["  ⎔ Commands: OK, HELP", "  ↳ Tip: use OK"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: "OK")
    result = prompt.ask("▶ ")
    assert result == "OK"
    out = capsys.readouterr().out
    assert "Commands: OK, HELP" in out
    assert "Tip: use OK" in out


def test_fallback_mac_obsidian_ctrl_p_opens_command(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    prompt.set_tab_handler(lambda: "HELP")
    monkeypatch.setenv("UDOS_KEYMAP_PROFILE", "mac-obsidian")
    monkeypatch.setattr(builtins, "input", lambda _prompt: "\x10")  # Ctrl+P
    result = prompt.ask("▶ ")
    assert result == "HELP"


def test_fallback_ctrl_o_routes_to_open_file_via_f2(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    called = {"count": 0}

    class _FakeFKey:
        handlers = {"F2": lambda: called.__setitem__("count", called["count"] + 1) or {"message": "opened"}}

    prompt.set_function_key_handler(_FakeFKey())
    monkeypatch.setenv("UDOS_KEYMAP_PROFILE", "mac-obsidian")
    inputs = iter(["\x0f", "STATUS"])  # Ctrl+O then normal command
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    result = prompt.ask("▶ ")
    assert result == "STATUS"
    assert called["count"] == 1


def test_fallback_ctrl_p_linux_keeps_nav_history_semantics(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    monkeypatch.setenv("UDOS_KEYMAP_PROFILE", "linux-default")
    inputs = iter(["\x10", "STATUS"])  # Ctrl+P becomes NAV_UP on linux profile
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    result = prompt.ask("▶ ")
    assert result == "STATUS"


def test_process_hotkey_text_submission_strips_literal_arrow_noise(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    monkeypatch.setenv("UDOS_KEYMAP_PROFILE", "mac-obsidian")
    result = prompt._process_hotkey_text_submission("· ▶ ^[[A^[[A^[[A")
    assert result == ""


def test_process_hotkey_text_submission_keeps_command_with_embedded_escape(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    monkeypatch.setenv("UDOS_KEYMAP_PROFILE", "mac-obsidian")
    result = prompt._process_hotkey_text_submission("STATUS ^[[A")
    assert result == "STATUS"


def test_consume_literal_escape_suffix_turns_into_nav(monkeypatch):
    prompt = SmartPrompt(use_fallback=True)
    prompt.input_history = ["HELP", "STATUS"]
    monkeypatch.setenv("UDOS_KEYMAP_PROFILE", "mac-obsidian")
    updated, handled = prompt._consume_literal_escape_suffix("▶ ", "^[[A")
    assert handled is True
    assert updated == "STATUS"
