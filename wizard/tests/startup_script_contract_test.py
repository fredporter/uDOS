from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_wizard_startup_script_targets_server_runtime_only():
    script = (_repo_root() / "wizard" / "web" / "start_wizard_web.sh").read_text(encoding="utf-8")

    assert "bin/udos" in script
    assert "udos\" wizard start" in script or "udos wizard start" in script
    assert "wizard.web.app" not in script
    assert "start_web_server" not in script


def test_embedded_wizard_web_app_module_removed():
    path = _repo_root() / "wizard" / "web" / "app.py"
    assert not path.exists()
