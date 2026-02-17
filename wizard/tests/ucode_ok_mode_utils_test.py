from wizard.routes import ucode_ok_mode_utils as utils


def test_load_and_write_ai_modes_config(monkeypatch, tmp_path):
    from core.services import logging_api

    monkeypatch.setattr(logging_api, "get_repo_root", lambda: tmp_path)
    payload = {"modes": {"ofvibe": {"default_models": {"core": "x"}}}}
    utils.write_ok_modes_config(payload)
    loaded = utils.load_ai_modes_config()
    assert loaded["modes"]["ofvibe"]["default_models"]["core"] == "x"


def test_get_ok_default_model_respects_dev_mode(monkeypatch):
    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"default_models": {"core": "core-m", "dev": "dev-m"}}}},
    )
    monkeypatch.delenv("UDOS_DEV_MODE", raising=False)
    assert utils.get_ok_default_model() == "core-m"

    monkeypatch.setenv("UDOS_DEV_MODE", "true")
    assert utils.get_ok_default_model() == "dev-m"


def test_ok_auto_fallback_defaults_to_true(monkeypatch):
    monkeypatch.setattr(utils, "load_ai_modes_config", lambda: {"modes": {"ofvibe": {}}})
    assert utils.ok_auto_fallback_enabled() is True

    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"auto_fallback": False}}},
    )
    assert utils.ok_auto_fallback_enabled() is False


def test_get_ok_local_status_variants(monkeypatch):
    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"ollama_endpoint": "http://ollama"}}},
    )
    monkeypatch.setattr(utils, "get_ok_default_model", lambda: "model-a")

    monkeypatch.setattr(utils, "fetch_ollama_models", lambda endpoint: {"reachable": False, "error": "down"})
    down = utils.get_ok_local_status()
    assert down["ready"] is False
    assert down["issue"] == "ollama down"

    monkeypatch.setattr(utils, "fetch_ollama_models", lambda endpoint: {"reachable": True, "models": ["other"]})
    missing = utils.get_ok_local_status()
    assert missing["ready"] is False
    assert missing["issue"] == "missing model"

    monkeypatch.setattr(utils, "fetch_ollama_models", lambda endpoint: {"reachable": True, "models": ["model-a"]})
    ready = utils.get_ok_local_status()
    assert ready["ready"] is True
    assert ready["issue"] is None


def test_get_ok_local_status_accepts_tagged_alias(monkeypatch):
    monkeypatch.setattr(
        utils,
        "load_ai_modes_config",
        lambda: {"modes": {"ofvibe": {"ollama_endpoint": "http://ollama"}}},
    )
    monkeypatch.setattr(utils, "get_ok_default_model", lambda: "devstral-small-2")
    monkeypatch.setattr(
        utils,
        "fetch_ollama_models",
        lambda endpoint: {"reachable": True, "models": ["devstral-small-2:latest"]},
    )
    ready = utils.get_ok_local_status()
    assert ready["ready"] is True
    assert ready["issue"] is None
