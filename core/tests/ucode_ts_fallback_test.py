import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_udos(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "bin/udos", *args],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
    )


def test_ucode_ts_subcommand_removed_from_v1_5_surface():
    res = _run_udos("ts")
    assert res.returncode != 0
    combined = f"{res.stdout}\n{res.stderr}"
    assert "invalid choice" in combined
    assert "ts" in combined


def test_udos_tui_subcommand_is_canonical_entrypoint():
    res = _run_udos("tui", "--help")
    assert res.returncode == 0
    combined = f"{res.stdout}\n{res.stderr}"
    assert "usage:" in combined.lower()
