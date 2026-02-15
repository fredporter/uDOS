from pathlib import Path

from core.commands.destroy_handler_helpers import (
    build_destroy_help_text,
    build_nuclear_confirmation_text,
    destroy_menu_options,
    format_destroy_options,
    resolve_vault_root,
)


def test_destroy_menu_and_formatting():
    options = destroy_menu_options()
    formatted = format_destroy_options(options)
    assert any(option["id"] == 4 for option in options)
    assert "NUCLEAR RESET" in formatted


def test_help_and_confirmation_text():
    formatted = format_destroy_options(destroy_menu_options())
    help_text = build_destroy_help_text(formatted)
    confirm_text = build_nuclear_confirmation_text()
    assert "DESTROY COMMAND HELP" in help_text
    assert "NUCLEAR RESET CONFIRMATION" in confirm_text


def test_resolve_vault_root_default(monkeypatch, tmp_path):
    monkeypatch.delenv("VAULT_ROOT", raising=False)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    path = resolve_vault_root(repo_root)
    assert path == Path(repo_root) / "memory" / "vault"

