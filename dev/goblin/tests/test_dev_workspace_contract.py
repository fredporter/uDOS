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
