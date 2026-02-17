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
