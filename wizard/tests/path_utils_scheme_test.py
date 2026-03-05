from wizard.services import path_utils


def test_logs_dir_defaults_to_memory_logs(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(path_utils, "get_config", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(path_utils, "_load_wizard_config", lambda: {})
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)

    logs_dir = path_utils.get_logs_dir()

    assert logs_dir == tmp_path / "memory" / "logs"
    assert logs_dir.is_dir()


def test_logs_dir_ignores_config_and_env_override_in_strict_mode(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(path_utils, "get_config", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        path_utils,
        "_load_wizard_config",
        lambda: {"file_locations": {"logs_root": ".runtime/logs"}},
    )
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)
    monkeypatch.setenv("UDOS_LOGS_DIR", ".env-logs")

    logs_dir = path_utils.get_logs_dir()

    assert logs_dir == tmp_path / "memory" / "logs"
    assert logs_dir.is_dir()


def test_artifacts_and_test_run_paths_default_under_dot_artifacts(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(path_utils, "get_config", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(path_utils, "_load_wizard_config", lambda: {})
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)

    artifacts_dir = path_utils.get_artifacts_dir()
    test_runs_dir = path_utils.get_test_runs_dir()

    assert artifacts_dir == tmp_path / ".artifacts"
    assert test_runs_dir == tmp_path / ".artifacts" / "test-runs"
    assert artifacts_dir.is_dir()
    assert test_runs_dir.is_dir()


def test_memory_and_vault_dirs_honor_config_overrides(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(path_utils, "get_config", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        path_utils,
        "_load_wizard_config",
        lambda: {"file_locations": {"memory_root": ".runtime/memory", "vault_root": ".runtime/vault"}},
    )
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)

    memory_dir = path_utils.get_memory_dir()
    vault_dir = path_utils.get_vault_dir()

    assert memory_dir == tmp_path / ".runtime" / "memory"
    assert vault_dir == tmp_path / ".runtime" / "vault"
    assert memory_dir.is_dir()
    assert vault_dir.is_dir()


def test_memory_and_vault_dirs_honor_env_overrides(tmp_path, monkeypatch) -> None:
    env_values = {
        "UDOS_MEMORY_ROOT": str(tmp_path / "custom-memory"),
        "VAULT_ROOT": str(tmp_path / "custom-vault"),
    }
    monkeypatch.setattr(path_utils, "get_config", lambda key, *_args, **_kwargs: env_values.get(key))
    monkeypatch.setattr(path_utils, "_load_wizard_config", lambda: {})
    monkeypatch.setattr(path_utils, "get_repo_root", lambda: tmp_path)

    memory_dir = path_utils.get_memory_dir()
    vault_dir = path_utils.get_vault_dir()

    assert memory_dir == tmp_path / "custom-memory"
    assert vault_dir == tmp_path / "custom-vault"
    assert memory_dir.is_dir()
    assert vault_dir.is_dir()
