import os
import stat
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _make_failing_node(tmp_path: Path) -> None:
    node_path = tmp_path / "node"
    node_path.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    node_path.chmod(node_path.stat().st_mode | stat.S_IXUSR)


def _run_ucli_ts(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    _make_failing_node(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:/usr/bin:/bin"
    env["UDOS_HOME_ROOT_ALLOW_OUTSIDE"] = "1"
    env["UDOS_QUIET"] = "1"
    return subprocess.run(
        ["bash", "bin/ucli", "ts", *args],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        env=env,
    )


def test_ucli_ts_no_args_missing_node_falls_back_with_message(tmp_path: Path):
    res = _run_ucli_ts(tmp_path)
    assert res.returncode == 0
    combined = f"{res.stdout}\n{res.stderr}"
    assert "Node runtime not detected. Falling back to core mode." in combined
    assert "Run from an interactive terminal to open core mode." in combined


def test_ucli_ts_verify_missing_node_prints_equivalent_core_command(tmp_path: Path):
    res = _run_ucli_ts(tmp_path, "verify")
    assert res.returncode == 0
    combined = f"{res.stdout}\n{res.stderr}"
    assert "Node runtime not detected. Falling back to core mode." in combined
    assert "Equivalent core command: VERIFY" in combined
