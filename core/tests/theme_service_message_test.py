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


def test_theme_service_supports_new_simple_vocab_profiles(monkeypatch):
    monkeypatch.delenv("UDOS_TUI_LEGACY_REPLACEMENTS", raising=False)
    svc = ThemeService()
    sample = "Tip: Check Wizard status.\nHealth: stable."

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "fantasy")
    themed_fantasy = svc.format(sample)
    assert "Quest Tip:" in themed_fantasy
    assert "Arcane Ops status." in themed_fantasy
    assert "Guild Health:" in themed_fantasy

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "roleplay")
    themed_role = svc.format(sample)
    assert "Role Tip:" in themed_role
    assert "Narrator Ops status." in themed_role
    assert "Party Health:" in themed_role

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "explorer")
    themed_explorer = svc.format(sample)
    assert "Expedition Tip:" in themed_explorer
    assert "Survey Ops status." in themed_explorer
    assert "Field Health:" in themed_explorer

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "scientist")
    themed_science = svc.format(sample)
    assert "Lab Tip:" in themed_science
    assert "Research Ops status." in themed_science
    assert "Systems Health:" in themed_science

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "pilot")
    themed_pilot = svc.format(sample)
    assert "Cockpit Tip:" in themed_pilot
    assert "Flight Ops status." in themed_pilot
    assert "Flight Health:" in themed_pilot

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "captainsailor")
    themed_captain = svc.format(sample)
    assert "Bridge Tip:" in themed_captain
    assert "Deck Ops status." in themed_captain
    assert "Crew Health:" in themed_captain

    monkeypatch.setenv("UDOS_TUI_MESSAGE_THEME", "pirate")
    themed_pirate = svc.format(sample)
    assert "Raid Tip:" in themed_pirate
    assert "Corsair Ops status." in themed_pirate
    assert "Hull Health:" in themed_pirate
