from __future__ import annotations

from pathlib import Path

from core.commands.binder_handler import BinderHandler
from core.services.vibe_binder_service import DevModeToolBinderService, VibeBinderService


def test_canonical_binder_service_alias_is_stable() -> None:
    assert DevModeToolBinderService is VibeBinderService


def test_binder_import_research_creates_imported_move(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "core.services.vibe_binder_service.get_vault_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "core.services.vibe_binder_service.get_udos_root",
        lambda: tmp_path,
    )
    service = DevModeToolBinderService()
    service.initialize_project("binder-research", "Binder Research", template="research_project")

    note_root = tmp_path / "memory" / "bank" / "knowledge" / "user" / "research"
    note_root.mkdir(parents=True, exist_ok=True)
    note_path = note_root / "note-binder.md"
    note_path.write_text(
        "---\nudos_id: \"note-binder\"\n---\n\n# Binder Research Note\n\nCompare local setup budget.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "core.commands.binder_handler.get_binder_service",
        lambda: service,
    )
    handler = BinderHandler()

    result = handler.handle(
        "BINDER",
        ["IMPORT-RESEARCH", "binder-research", "note-binder"],
        None,
        None,
    )

    assert result["status"] == "success"
    imported_path = tmp_path / "@binders" / "binder-research" / "research" / "research" / "note-binder.md"
    assert imported_path.exists()
    tasks = service.list_moves("binder-research")
    assert tasks["count"] >= 1
    assert any(move.get("source") == "research" for move in tasks["moves"])
