from __future__ import annotations

from pathlib import Path

from core.services.logic_assist_setup import inspect_logic_assist_setup, run_logic_assist_setup


def _seed_logic_assist_settings(repo_root: Path) -> None:
    settings_path = (
        repo_root
        / "core"
        / "framework"
        / "seed"
        / "bank"
        / "typo-workspace"
        / "settings"
        / "logic-assist.md"
    )
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        "\n".join(
            [
                "# Logic Assist Settings Template",
                "",
                "- local_runtime: gpt4all",
                "- local_model_name: local-test.gguf",
                "- local_model_path: memory/models/gpt4all",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_inspect_logic_assist_setup_reports_expected_paths(tmp_path) -> None:
    _seed_logic_assist_settings(tmp_path)

    status = inspect_logic_assist_setup(tmp_path)

    assert status["runtime"] == "gpt4all"
    assert str(status["model_path"]).endswith("/memory/models/gpt4all/local-test.gguf")
    assert str(status["guidance_path"]).endswith("/memory/models/gpt4all/README.md")
    assert status["model_present"] is False


def test_run_logic_assist_setup_writes_guidance_when_model_missing(tmp_path, monkeypatch) -> None:
    _seed_logic_assist_settings(tmp_path)
    monkeypatch.setattr("core.services.logic_assist_setup.shutil.which", lambda name: None)
    monkeypatch.setattr(
        "core.services.logic_assist_setup.subprocess.run",
        lambda *args, **kwargs: type("_Proc", (), {"returncode": 0, "stderr": "", "stdout": ""})(),
    )
    monkeypatch.setattr("core.services.logic_assist_setup.importlib.util.find_spec", lambda name: None)

    result = run_logic_assist_setup(tmp_path, log=lambda message: None)

    guidance_path = tmp_path / "memory" / "models" / "gpt4all" / "README.md"
    assert guidance_path.exists()
    assert "Place the configured GPT4All model file in this folder." in guidance_path.read_text(encoding="utf-8")
    assert result["status"]["guidance_present"] is True
    assert result["status"]["model_present"] is False
    assert any("Model file missing" in item for item in result["warnings"])
