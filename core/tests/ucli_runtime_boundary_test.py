import os
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _make_stub_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "udos-stub"
    (repo / "wizard").mkdir(parents=True, exist_ok=True)
    (repo / "uDOS.py").write_text("# stub repo marker\n", encoding="utf-8")
    (repo / "wizard" / "requirements.txt").write_text("fastapi==0.0.0\n", encoding="utf-8")
    return repo


def test_core_modules_import_with_system_python_no_venv():
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env["PYTHONNOUSERSITE"] = "1"
    res = subprocess.run(
        [
            "python3",
            "-c",
            "import core.commands.verify_handler, core.commands.draw_handler, core.services.ts_runtime_service",
        ],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0, res.stderr


def test_wizard_env_check_emits_install_guidance_when_missing(tmp_path: Path):
    stub_repo = _make_stub_repo(tmp_path)
    cmd = (
        "source bin/udos-common.sh; "
        f"export UDOS_ROOT='{stub_repo}'; "
        "ensure_wizard_env"
    )
    res = subprocess.run(
        ["bash", "-lc", cmd],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    assert res.returncode != 0
    combined = f"{res.stdout}\n{res.stderr}"
    assert "Wizard environment not installed. Run: ucli wizard install" in combined


def test_ucli_wizard_doctor_fails_when_wizard_venv_missing(tmp_path: Path):
    stub_repo = _make_stub_repo(tmp_path)
    env = os.environ.copy()
    env["UDOS_ROOT"] = str(stub_repo)
    env["UDOS_HOME_ROOT_ALLOW_OUTSIDE"] = "1"
    res = subprocess.run(
        ["bash", "bin/ucli", "wizard", "doctor"],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode != 0
    combined = f"{res.stdout}\n{res.stderr}"
    assert "Wizard environment not installed. Run: ucli wizard install" in combined
