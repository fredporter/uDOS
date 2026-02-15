from pathlib import Path

from core.commands.setup_handler_helpers import (
    clear_setup_env,
    detect_udos_root,
    initialize_env_from_example,
    load_setup_env_vars,
    setup_help_text,
)


def test_detect_udos_root_from_env(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "uDOS.py").write_text("# marker\n")
    monkeypatch.setenv("UDOS_ROOT", str(repo))
    detected = detect_udos_root()
    assert detected == repo


def test_initialize_load_and_clear_env(tmp_path):
    env_file = tmp_path / ".env"
    example = tmp_path / ".env.example"
    example.write_text('USER_NAME="demo"\nOTHER_KEY="keep"\n')

    initialize_env_from_example(env_file)
    vars_loaded = load_setup_env_vars(env_file)
    assert vars_loaded["USER_NAME"] == "demo"

    clear_setup_env(env_file)
    contents = env_file.read_text()
    assert "USER_NAME" not in contents
    assert "OTHER_KEY" in contents


def test_setup_help_text_has_usage():
    text = setup_help_text()
    assert "SETUP --help" in text
    assert "SETUP github" in text

