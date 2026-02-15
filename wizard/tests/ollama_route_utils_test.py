import subprocess

from fastapi import HTTPException

from wizard.routes import ollama_route_utils as utils


def test_validate_model_name_rejects_invalid_values():
    try:
        utils.validate_model_name("bad model name!")
        assert False, "Expected HTTPException for invalid model name"
    except HTTPException as exc:
        assert exc.status_code == 400


def test_get_installed_models_uses_cli_output(monkeypatch):
    class Result:
        returncode = 0
        stdout = "NAME ID SIZE MODIFIED\nmistral:latest abc 4GB 2d\n"

    def fake_run(*args, **kwargs):
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    payload = utils.get_installed_ollama_models_payload()
    assert payload["success"] is True
    assert payload["count"] == 1
    assert payload["models"][0]["name"] == "mistral:latest"


def test_get_installed_models_falls_back_to_api(monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError()

    def fake_api(path):
        assert path == "/api/tags"
        return {"models": [{"name": "mistral:latest", "size": 123, "modified_at": "now"}]}

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(utils, "ollama_api_request", fake_api)
    payload = utils.get_installed_ollama_models_payload()
    assert payload["success"] is True
    assert payload["count"] == 1
    assert payload["models"][0]["name"] == "mistral:latest"

