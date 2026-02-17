from pathlib import Path

from wizard.services.wizard_config import (
    load_wizard_config_data,
    save_wizard_config_data,
    resolve_wizard_config_path,
)


def test_load_wizard_config_data_returns_defaults_when_missing(tmp_path):
    config_path = tmp_path / "wizard.json"
    payload = load_wizard_config_data(path=config_path, defaults={"port": 8765})
    assert payload == {"port": 8765}


def test_load_wizard_config_data_merges_defaults(tmp_path):
    config_path = tmp_path / "wizard.json"
    config_path.write_text('{"debug": true}', encoding="utf-8")
    payload = load_wizard_config_data(
        path=config_path,
        defaults={"port": 8765, "debug": False},
    )
    assert payload == {"port": 8765, "debug": True}


def test_load_wizard_config_data_migrates_ai_gateway_flag(tmp_path):
    config_path = tmp_path / "wizard.json"
    config_path.write_text('{"ai_gateway_enabled": true}', encoding="utf-8")
    payload = load_wizard_config_data(path=config_path)
    assert payload["ai_gateway_enabled"] is True
    assert payload["ok_gateway_enabled"] is True


def test_save_wizard_config_data_roundtrip(tmp_path):
    config_path = tmp_path / "wizard.json"
    save_wizard_config_data({"host": "127.0.0.1", "port": 9000}, path=config_path)
    payload = load_wizard_config_data(path=config_path)
    assert payload == {"host": "127.0.0.1", "port": 9000}


def test_resolve_wizard_config_path_honors_env(monkeypatch):
    env_path = "/tmp/wizard-test-config.json"
    monkeypatch.setenv("WIZARD_CONFIG_PATH", env_path)
    assert resolve_wizard_config_path() == Path(env_path)
