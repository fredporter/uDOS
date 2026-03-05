from __future__ import annotations

from pathlib import Path

import pytest

from core.services.path_service import clear_repo_root_cache
from core.services.path_service import find_repo_root
from core.services.path_service import get_repo_root
from core.services.path_service import resolve_repo_path


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_repo_root_cache()
    yield
    clear_repo_root_cache()


def test_find_repo_root_from_nested_start_path(tmp_path: Path):
    repo = tmp_path / "repo"
    nested = repo / "wizard" / "services"
    nested.mkdir(parents=True)
    (repo / "uDOS.py").write_text("# marker\n", encoding="utf-8")

    resolved = find_repo_root(start_path=nested, marker="uDOS.py")
    assert resolved == repo


def test_get_repo_root_honors_relative_udos_root(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "uDOS.py").write_text("# marker\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("UDOS_ROOT", "repo")

    resolved = get_repo_root(marker="uDOS.py")
    assert resolved == repo


def test_resolve_repo_path_uses_repo_root_for_relative_paths(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "uDOS.py").write_text("# marker\n", encoding="utf-8")

    monkeypatch.setenv("UDOS_ROOT", str(repo))

    resolved = resolve_repo_path("memory/logs", marker="uDOS.py")
    assert resolved == repo / "memory" / "logs"


def test_get_repo_root_ignores_invalid_udos_root_and_falls_back(tmp_path: Path, monkeypatch):
    bad_root = tmp_path / "bad"
    bad_root.mkdir(parents=True)
    monkeypatch.setenv("UDOS_ROOT", str(bad_root))
    resolved = get_repo_root(marker="uDOS.py")
    assert (resolved / "uDOS.py").exists()
