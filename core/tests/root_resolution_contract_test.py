from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from core.commands.config_handler import ConfigHandler
from core.services import registry


def test_config_edit_uses_canonical_repo_root(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    config_dir = repo_root / "wizard" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "wizard.json").write_text("{}", encoding="utf-8")

    handler = ConfigHandler()

    monkeypatch.setattr("core.commands.config_handler.get_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        "core.services.unified_config_loader.get_config",
        lambda key, default="": "true-editor",
    )

    calls: dict[str, object] = {}

    def _fake_run(cmd, check):
        calls["cmd"] = cmd
        calls["check"] = check
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("subprocess.run", _fake_run)

    result = handler._edit_config("wizard.json")

    assert result["status"] == "success"
    assert calls["cmd"] == ["true-editor", str(config_dir / "wizard.json")]
    assert calls["check"] is True


def test_registry_repo_root_helper_uses_canonical_service(tmp_path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(registry, "get_repo_root", lambda: repo_root)
    original_sys_path = list(registry.sys.path)
    registry.sys.path[:] = []
    try:
        resolved = registry._ensure_repo_root_on_sys_path()
        assert resolved == repo_root
        assert registry.sys.path[0] == str(repo_root)
    finally:
        registry.sys.path[:] = original_sys_path
