from __future__ import annotations

from pathlib import Path

from core.services.self_healer import SelfHealer


def test_get_logic_assist_model_path_uses_repo_relative_root() -> None:
    healer = SelfHealer(component="core", auto_repair=False)
    fields = {
        "local_model_name": "model.gguf",
        "local_model_path": "memory/models/gpt4all",
    }
    assert healer._get_logic_assist_model_path(fields) == (
        healer.repo_root / "memory" / "models" / "gpt4all" / "model.gguf"
    )


def test_check_logic_assist_adds_missing_model_issue(monkeypatch) -> None:
    monkeypatch.setattr(
        SelfHealer,
        "_load_logic_assist_fields",
        lambda self: {
            "local_runtime": "gpt4all",
            "local_model_name": "devstral-small-2.gguf",
            "local_model_path": "memory/models/gpt4all",
        },
    )
    monkeypatch.setattr("core.services.self_healer.importlib.util.find_spec", lambda name: object())

    healer = SelfHealer(component="core", auto_repair=False)
    healer._check_logic_assist()

    issue = next(
        (item for item in healer.issues if item.repair_action == "place_configured_model"),
        None,
    )
    assert issue is not None
    assert issue.details["model"] == "devstral-small-2.gguf"


def test_check_logic_assist_adds_missing_package_issue(monkeypatch) -> None:
    model_root = Path("/tmp/gpt4all")
    monkeypatch.setattr(
        SelfHealer,
        "_load_logic_assist_fields",
        lambda self: {
            "local_runtime": "gpt4all",
            "local_model_name": "devstral-small-2.gguf",
            "local_model_path": str(model_root),
        },
    )
    monkeypatch.setattr("core.services.self_healer.importlib.util.find_spec", lambda name: None)

    healer = SelfHealer(component="core", auto_repair=False)
    healer._check_logic_assist()

    issue = next(
        (
            item
            for item in healer.issues
            if item.repair_action == "install_logic_assist_dependencies"
        ),
        None,
    )
    assert issue is not None
    assert issue.details["runtime"] == "gpt4all"
