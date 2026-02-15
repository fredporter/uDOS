from pathlib import Path

from core.services import destructive_ops


def test_resolve_vault_root_prefers_env(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "custom-vault"))
    assert destructive_ops.resolve_vault_root(repo_root) == Path(
        tmp_path / "custom-vault"
    )


def test_remove_path_handles_file_and_directory(tmp_path):
    file_path = tmp_path / "a.txt"
    file_path.write_text("x", encoding="utf-8")
    assert destructive_ops.remove_path(file_path) is True
    assert not file_path.exists()

    dir_path = tmp_path / "dir"
    (dir_path / "nested").mkdir(parents=True, exist_ok=True)
    assert destructive_ops.remove_path(dir_path) is True
    assert not dir_path.exists()
    assert destructive_ops.remove_path(dir_path) is False


def test_scrub_directory_recreates(tmp_path):
    path = tmp_path / "target"
    (path / "sub").mkdir(parents=True, exist_ok=True)
    (path / "sub" / "file.txt").write_text("1", encoding="utf-8")

    destructive_ops.scrub_directory(path, recreate=True)
    assert path.exists()
    assert list(path.iterdir()) == []


def test_ensure_memory_layout_creates_defaults(tmp_path):
    memory_root = tmp_path / "memory"
    destructive_ops.ensure_memory_layout(memory_root)
    assert (memory_root / "logs").exists()
    assert (memory_root / "bank").exists()
    assert (memory_root / "private").exists()
    assert (memory_root / "wizard").exists()


def test_wipe_json_config_dir_keeps_allowlist(tmp_path):
    config = tmp_path / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "a.json").write_text("{}", encoding="utf-8")
    (config / "b.json").write_text("{}", encoding="utf-8")
    (config / "keep.json").write_text("{}", encoding="utf-8")
    (config / "note.txt").write_text("x", encoding="utf-8")

    removed = destructive_ops.wipe_json_config_dir(config, keep_files={"keep.json"})
    assert removed == 2
    assert not (config / "a.json").exists()
    assert not (config / "b.json").exists()
    assert (config / "keep.json").exists()
    assert (config / "note.txt").exists()
