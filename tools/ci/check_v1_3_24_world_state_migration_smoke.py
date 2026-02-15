#!/usr/bin/env python3
"""v1.3.24 world-state migration smoke gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "core/tests/v1_3_24_world_state_migration_smoke_test.py",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"world-state migration smoke failed:\n{details}")
    print(proc.stdout.strip())
    print("[world-state-migration-smoke-v1.3.24] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

