from wizard.routes import ucode_ok_mode_utils as utils


def test_load_and_write_ok_modes_config(monkeypatch, tmp_path):
    from core.services import logging_api

    monkeypatch.setattr(logging_api, "get_repo_root", lambda: tmp_path)
    payload = {"modes": {"ofvibe": {"default_models": {"core": "x"}}}}
    utils.write_ok_modes_config(payload)
    loaded = utils.load_ok_modes_config()
    assert loaded["modes"]["ofvibe"]["default_models"]["core"] == "x"


def test_get_ok_default_model_respects_dev_mode(monkeypatch):
    monkeypatch.setattr(
        utils,
        "load_ok_modes_config",
        lambda: {"modes": {"ofvibe": {"default_models": {"core": "core-m", "dev": "dev-m"}}}},
    )
    monkeypatch.delenv("UDOS_DEV_MODE", raising=False)
    assert utils.get_ok_default_model() == "core-m"

    monkeypatch.setenv("UDOS_DEV_MODE", "true")
    assert utils.get_ok_default_model() == "dev-m"


def test_ok_auto_fallback_defaults_to_true(monkeypatch):
    monkeypatch.setattr(utils, "load_ok_modes_config", lambda: {"modes": {"ofvibe": {}}})
    assert utils.ok_auto_fallback_enabled() is True

    monkeypatch.setattr(
        utils,
        "load_ok_modes_config",
        lambda: {"modes": {"ofvibe": {"auto_fallback": False}}},
    )
    assert utils.ok_auto_fallback_enabled() is False


def test_get_ok_local_status_variants(monkeypatch):
    monkeypatch.setattr(utils, "get_ok_default_model", lambda: "model-a")

    class _LogicAssist:
        def __init__(self, local):
            self._local = local

        def get_status(self):
            return self._local

    monkeypatch.setattr(
        utils,
        "get_logic_assist_service",
        lambda: _LogicAssist(
            {
                "local": {
                    "ready": False,
                    "issue": "gpt4all package unavailable",
                    "model": "model-a",
                    "model_path": "/tmp/model-a.gguf",
                    "runtime": "gpt4all",
                },
                "context": {"hash": "hash-a", "count": 2},
                "conversations": {"stored": 1},
                "cache": {"entries": 3},
            }
        ),
    )
    down = utils.get_ok_local_status()
    assert down["ready"] is False
    assert down["issue"] == "local runtime down"
    assert down["context_hash"] == "hash-a"
    assert down["context_files"] == 2
    assert down["conversation_store"] == 1
    assert down["cache_entries"] == 3

    monkeypatch.setattr(
        utils,
        "get_logic_assist_service",
        lambda: _LogicAssist(
            {
                "local": {
                    "ready": False,
                    "issue": "gpt4all model missing",
                    "model": "model-a",
                    "model_path": "/tmp/model-a.gguf",
                    "runtime": "gpt4all",
                },
                "context": {"hash": "hash-b", "count": 3},
                "conversations": {"stored": 0},
                "cache": {"entries": 0},
            }
        ),
    )
    missing = utils.get_ok_local_status()
    assert missing["ready"] is False
    assert missing["issue"] == "missing model"

    monkeypatch.setattr(
        utils,
        "get_logic_assist_service",
        lambda: _LogicAssist(
            {
                "local": {
                    "ready": True,
                    "issue": None,
                    "model": "model-a",
                    "model_path": "/tmp/model-a.gguf",
                    "runtime": "gpt4all",
                },
                "context": {"hash": "hash-c", "count": 4},
                "conversations": {"stored": 2},
                "cache": {"entries": 1},
            }
        ),
    )
    ready = utils.get_ok_local_status()
    assert ready["ready"] is True
    assert ready["issue"] is None
    assert ready["context_hash"] == "hash-c"
    assert ready["context_files"] == 4
    assert ready["conversation_store"] == 2


def test_get_ok_local_status_accepts_tagged_alias(monkeypatch):
    monkeypatch.setattr(utils, "get_ok_default_model", lambda: "devstral-small-2")

    class _LogicAssist:
        def get_status(self):
            return {
                "local": {
                    "ready": True,
                    "issue": None,
                    "model": "devstral-small-2",
                    "model_path": "/tmp/devstral-small-2.gguf",
                    "runtime": "gpt4all",
                },
                "context": {"hash": "hash-dev", "count": 5},
                "conversations": {"stored": 3},
                "cache": {"entries": 4},
            }

    monkeypatch.setattr(utils, "get_logic_assist_service", lambda: _LogicAssist())

    ready = utils.get_ok_local_status()
    assert ready["ready"] is True
    assert ready["issue"] is None
    assert ready["context_hash"] == "hash-dev"
