#!/usr/bin/env python3
"""v1.4.0 TOYBOX FastAPI lifespan readiness gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET = REPO / "wizard" / "services" / "toybox" / "base_adapter.py"


def _assert_source_shape() -> None:
    src = TARGET.read_text(encoding="utf-8")
    if "@app.on_event(\"startup\")" in src or "@app.on_event(\"shutdown\")" in src:
        raise RuntimeError("TOYBOX adapter still uses deprecated @app.on_event hooks")
    if "lifespan=lifespan" not in src:
        raise RuntimeError("TOYBOX adapter FastAPI app missing lifespan handler wiring")
    if "asynccontextmanager" not in src:
        raise RuntimeError("TOYBOX adapter missing asynccontextmanager lifespan implementation")


def _run_lifecycle_tests() -> None:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "wizard/tests/toybox_adapter_lifecycle_test.py",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"toybox adapter lifecycle tests failed:\n{details}")
    print(proc.stdout.strip())


def main() -> int:
    _assert_source_shape()
    _run_lifecycle_tests()
    print("[toybox-lifespan-readiness-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
