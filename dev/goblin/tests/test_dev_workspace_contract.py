from __future__ import annotations

from pathlib import Path

from wizard.routes import ucode_routes
from wizard.services.dev_extension_service import DevExtensionService
from wizard.services import dev_extension_service, dev_mode_service
from wizard.services.dev_mode_service import DevModeService


def test_dev_extension_service_defaults_to_canonical_repo_root(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    monkeypatch.setattr(
        "wizard.services.dev_extension_service.get_repo_root",
        lambda: repo_root,
    )
    monkeypatch.setattr(
        "wizard.services.dev_extension_service.get_dev_mode_service",
        lambda: object(),
    )

    service = DevExtensionService()

    assert service.repo_root == repo_root
    assert service.dev_root == repo_root / "dev"


def test_dev_mode_service_defaults_to_canonical_repo_root(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    monkeypatch.setattr(
        "wizard.services.dev_mode_service.get_repo_root",
        lambda: repo_root,
    )

    service = DevModeService()

    assert service.repo_root == repo_root
    assert service.wizard_root == repo_root
    assert service._dev_root() == repo_root / "dev"


def test_local_logic_assist_builder_uses_canonical_repo_root(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    captured: dict[str, object] = {}

    class FakeProfile:
        def __init__(self, *, local_model_name: str = "base.gguf") -> None:
            self.local_model_name = local_model_name

        def to_dict(self) -> dict[str, str]:
            return {"local_model_name": self.local_model_name}

    class FakeAssist:
        def __init__(self, profile, root: Path) -> None:
            captured["profile"] = profile
            captured["root"] = root

    monkeypatch.setattr(ucode_routes, "get_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        "wizard.services.local_model_gpt4all.GPT4AllLocalAssist",
        FakeAssist,
    )

    assist = ucode_routes._build_local_logic_assist(FakeProfile(), model="override.gguf")

    assert isinstance(assist, FakeAssist)
    assert captured["root"] == repo_root
    assert getattr(captured["profile"], "local_model_name") == "override.gguf"


def test_dev_mode_service_singleton_refreshes_when_repo_root_changes(tmp_path, monkeypatch) -> None:
    first_root = tmp_path / "repo-a"
    second_root = tmp_path / "repo-b"
    dev_mode_service._dev_mode_service = None
    monkeypatch.setattr(
        "wizard.services.dev_mode_service.get_repo_root",
        lambda: first_root,
    )

    first = dev_mode_service.get_dev_mode_service()

    monkeypatch.setattr(
        "wizard.services.dev_mode_service.get_repo_root",
        lambda: second_root,
    )
    second = dev_mode_service.get_dev_mode_service()

    assert first.repo_root == first_root
    assert second.repo_root == second_root
    assert first is not second


def test_dev_extension_service_singleton_refreshes_when_repo_root_changes(tmp_path, monkeypatch) -> None:
    first_root = tmp_path / "repo-a"
    second_root = tmp_path / "repo-b"
    dev_extension_service._dev_extension_service = None
    monkeypatch.setattr(
        "wizard.services.dev_extension_service.get_repo_root",
        lambda: first_root,
    )
    monkeypatch.setattr(
        "wizard.services.dev_extension_service.get_dev_mode_service",
        lambda repo_root=None: object(),
    )

    first = dev_extension_service.get_dev_extension_service()

    monkeypatch.setattr(
        "wizard.services.dev_extension_service.get_repo_root",
        lambda: second_root,
    )
    second = dev_extension_service.get_dev_extension_service()

    assert first.repo_root == first_root
    assert second.repo_root == second_root
    assert first is not second


def test_dev_mode_requirements_reuse_dev_extension_framework_status(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    monkeypatch.setattr(
        "wizard.services.dev_mode_service.get_repo_root",
        lambda: repo_root,
    )

    service = DevModeService()

    monkeypatch.setattr(
        "wizard.services.dev_extension_service.get_dev_mode_service",
        lambda repo_root=None: object(),
    )
    framework_status = {
        "workspace_alias": "@dev",
        "dev_root": str(repo_root / "dev"),
        "dev_root_present": True,
        "framework_manifest_path": str(repo_root / "dev" / "extension.json"),
        "framework_manifest_present": True,
        "required_files": ["AGENTS.md", "goblin/tests/README.md"],
        "missing_files": ["goblin/tests/README.md"],
        "framework_ready": False,
        "tracked_sync_paths": ["ops", "docs", "goblin", "goblin/tests"],
        "goblin_layers": {
            "server": str(repo_root / "dev" / "goblin" / "server"),
            "seed": str(repo_root / "dev" / "goblin" / "seed"),
            "scenarios": str(repo_root / "dev" / "goblin" / "scenarios"),
            "test_vault": str(repo_root / "dev" / "goblin" / "test-vault"),
            "tests": str(repo_root / "dev" / "goblin" / "tests"),
        },
        "ops_paths": {
            "root": str(repo_root / "dev" / "ops"),
            "project": str(repo_root / "dev" / "ops" / "project.json"),
            "tasks": str(repo_root / "dev" / "ops" / "tasks.md"),
            "tasks_json": str(repo_root / "dev" / "ops" / "tasks.json"),
            "completed": str(repo_root / "dev" / "ops" / "completed.json"),
            "devlog": str(repo_root / "dev" / "ops" / "DEVLOG.md"),
        },
        "local_only_dirs": {
            "files": {"path": str(repo_root / "dev" / "files"), "present": False},
            "relecs": {"path": str(repo_root / "dev" / "relecs"), "present": False},
            "dev-work": {"path": str(repo_root / "dev" / "dev-work"), "present": False},
            "testing": {"path": str(repo_root / "dev" / "testing"), "present": False},
        },
    }

    monkeypatch.setattr(
        "wizard.services.dev_extension_service.DevExtensionService.framework_status",
        lambda self: framework_status,
    )

    requirements = service.check_requirements(force=True)

    assert requirements["dev_template_present"] is False
    assert requirements["framework_ready"] is False
    assert requirements["required_files"] == ["AGENTS.md", "goblin/tests/README.md"]
    assert requirements["missing_files"] == ["goblin/tests/README.md"]
