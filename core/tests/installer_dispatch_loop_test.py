"""Legacy Linux package installer coverage was retired for v1.5 stable."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_linux_package_installer_is_composted() -> None:
    assert not (REPO_ROOT / "distribution" / "installer.sh").exists()
    assert not (REPO_ROOT / "distribution" / "install-udos-linux.sh").exists()
    assert (
        REPO_ROOT / ".compost" / "2026-03-04" / "archive" / "distribution" / "installer.sh"
    ).exists()
