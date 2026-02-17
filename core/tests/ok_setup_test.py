import json
from pathlib import Path

from core.services.ok_setup import _load_ok_modes_config_for_setup


def test_load_ok_modes_config_for_setup_recovers_invalid_json(tmp_path: Path):
    config_path = tmp_path / "ok_modes.json"
    config_path.write_text("")

    config, warnings = _load_ok_modes_config_for_setup(config_path)

    assert config == {"modes": {}}
    assert any("Recovered invalid ok_modes.json" in warning for warning in warnings)
    backups = list(tmp_path.glob("ok_modes.invalid-*.json"))
    assert backups


def test_load_ok_modes_config_for_setup_valid_object(tmp_path: Path):
    config_path = tmp_path / "ok_modes.json"
    payload = {"modes": {"ofvibe": {"default_models": {"core": "m1"}}}}
    config_path.write_text(json.dumps(payload))

    config, warnings = _load_ok_modes_config_for_setup(config_path)

    assert config == payload
    assert warnings == []
