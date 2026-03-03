from __future__ import annotations

from pathlib import Path

from core.services import maintenance_utils


def test_markdown_library_housekeeping_moves_unsupported_files(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    compost = repo / ".compost"
    compost.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(maintenance_utils, "get_repo_root", lambda: repo)
    monkeypatch.setattr(maintenance_utils, "get_vault_root", lambda: tmp_path / "vault")

    vault = tmp_path / "vault"
    vault.mkdir(parents=True, exist_ok=True)
    (vault / "note.md").write_text("# note\n", encoding="utf-8")
    (vault / "note.json").write_text("{}\n", encoding="utf-8")
    (vault / "bad.bin").write_text("bin", encoding="utf-8")
    (vault / "__pycache__").mkdir(parents=True, exist_ok=True)
    (vault / "__pycache__" / "x.pyc").write_text("x", encoding="utf-8")

    preview = maintenance_utils.run_housekeeping("vault", apply=False)
    assert preview["candidate_count"] >= 2

    applied = maintenance_utils.run_housekeeping("vault", apply=True)
    assert applied["moved"] >= 2
    assert (vault / "note.md").exists()
    assert (vault / "note.json").exists()
    assert not (vault / "bad.bin").exists()
    assert not (vault / "__pycache__").exists()


def test_compost_cleanup_prunes_old_versions_by_overflow(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    compost_root = repo / ".compost"
    archive_root = compost_root / "2026-03-03" / "archive" / "processed"
    archive_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(maintenance_utils, "get_repo_root", lambda: repo)
    monkeypatch.setattr(maintenance_utils, "get_config", lambda key, default="": "2" if key == "UDOS_COMPOST_KEEP_VERSIONS" else default)

    names = [
        "20260303-100000-note.md",
        "20260303-110000-note.md",
        "20260303-120000-note.md",
    ]
    for name in names:
        (archive_root / name).write_text(name, encoding="utf-8")

    result = maintenance_utils.compost_cleanup(days=3650, dry_run=False)
    remaining = sorted(path.name for path in archive_root.glob("*.md"))

    assert result["version_pruned"] == 1
    assert len(remaining) == 2


def test_dev_housekeeping_only_targets_local_work_and_transient_dirs(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    dev_root = repo / "dev"
    (dev_root / "docs").mkdir(parents=True, exist_ok=True)
    (dev_root / "files").mkdir(parents=True, exist_ok=True)
    (dev_root / "node_modules").mkdir(parents=True, exist_ok=True)
    (dev_root / "AGENTS.md").write_text("# ok\n", encoding="utf-8")
    (dev_root / "files" / "draft.md").write_text("# draft\n", encoding="utf-8")
    (dev_root / "files" / "bad.exe").write_text("x", encoding="utf-8")
    monkeypatch.setattr(maintenance_utils, "get_repo_root", lambda: repo)

    report = maintenance_utils.run_housekeeping("dev", apply=True)

    assert report["moved"] >= 2
    assert (dev_root / "AGENTS.md").exists()
    assert (dev_root / "files" / "draft.md").exists()
    assert not (dev_root / "files" / "bad.exe").exists()
    assert not (dev_root / "node_modules").exists()
