from __future__ import annotations

from pathlib import Path

from core.services.mission_templates import ProjectInitializer
from core.services.vibe_binder_service import DevModeToolBinderService, VibeBinderService


def test_canonical_binder_service_alias_is_stable() -> None:
    assert DevModeToolBinderService is VibeBinderService


def test_project_initializer_writes_validated_project_and_tasks(tmp_path: Path) -> None:
    result = ProjectInitializer.initialize_project(
        project_id="binder-alpha",
        vault_root=str(tmp_path),
        template_type="software_project",
        with_seed_tasks=True,
    )

    assert result["status"] == "success"
    assert (tmp_path / "@binders" / "binder-alpha" / "project.json").exists()
    assert (tmp_path / "@binders" / "binder-alpha" / "tasks.json").exists()
    assert (tmp_path / "@binders" / "binder-alpha" / "completed.json").exists()


def test_vibe_binder_service_rejects_invalid_project_payload(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "core.services.vibe_binder_service.get_vault_root",
        lambda: tmp_path,
    )
    service = DevModeToolBinderService()

    ok = service._save_mission_file(
        "binder-beta",
        "project.json",
        {"description": "missing id/name"},
    )

    assert ok is False


def test_vibe_binder_service_rejects_invalid_tasks_payload(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "core.services.vibe_binder_service.get_vault_root",
        lambda: tmp_path,
    )
    service = DevModeToolBinderService()

    ok = service._save_mission_file(
        "binder-gamma",
        "tasks.json",
        {"tasks": [{"title": "missing id", "status": "todo"}]},
    )

    assert ok is False


def test_vibe_binder_service_rejects_invalid_completed_payload(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "core.services.vibe_binder_service.get_vault_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "core.services.vibe_binder_service.get_udos_root",
        lambda: tmp_path,
    )
    service = DevModeToolBinderService()

    ok = service._save_mission_file(
        "binder-delta",
        "completed.json",
        {"completed": [{"description": "missing id and title"}]},
    )

    assert ok is False
