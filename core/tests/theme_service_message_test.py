from core.services.theme_service import ThemeService


def test_theme_service_uses_simple_map_level_vocab(monkeypatch):
    monkeypatch.delenv("UDOS_TUI_LEGACY_REPLACEMENTS", raising=False)
    monkeypatch.delenv("UDOS_TUI_MESSAGE_THEME", raising=False)
    monkeypatch.delenv("UDOS_TUI_MAP_LEVEL", raising=False)

    svc = ThemeService()
    text = "Tip: Check Wizard status.\nHealth: stable."
    themed = svc.format(text, map_level="galaxy")

    assert "Galaxy Tip:" in themed
    assert "Star Ops status." in themed
    assert "Fleet Health:" in themed


def test_theme_service_allows_message_theme_override(monkeypatch):
    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "dungeon")
    monkeypatch.delenv("UDOS_TUI_LEGACY_REPLACEMENTS", raising=False)

    svc = ThemeService()
    themed = svc.format("Tip: Repair via Wizard.")

    assert "Delve Tip:" in themed
    assert "Dungeon Ops." in themed


def test_theme_service_legacy_mode_keeps_broad_replacements(monkeypatch):
    monkeypatch.setenv("UDOS_TUI_LEGACY_REPLACEMENTS", "1")
    monkeypatch.delenv("UDOS_TUI_MESSAGE_THEME", raising=False)

    svc = ThemeService()
    svc.load_theme("dungeon")
    themed = svc.format("uDOS Wizard Self-Heal")

    assert "NightVault" in themed
    assert "Golem" in themed
    assert "Bone-Mend" in themed


def test_theme_service_supports_other_simple_vocab_profiles(monkeypatch):
    monkeypatch.delenv("UDOS_TUI_LEGACY_REPLACEMENTS", raising=False)
    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "lonely-planet")

    svc = ThemeService()
    themed = svc.format("Tip: Check Wizard status.\nHealth: stable.")
    assert "Trail Tip:" in themed
    assert "Guide Ops status." in themed
    assert "Camp Health:" in themed

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "hitchhikers")
    themed_hitch = svc.format("Tip: Check Wizard status.\nHealth: stable.")
    assert "42 Tip:" in themed_hitch
    assert "Guide Console status." in themed_hitch
    assert "Ship Health:" in themed_hitch
