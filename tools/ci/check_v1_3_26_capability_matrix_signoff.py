#!/usr/bin/env python3
"""v1.3.26 capability matrix sign-off across Core/Wizard/TOYBOX lanes."""

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
        "core/tests/v1_3_21_parity_gate_test.py",
        "core/tests/v1_3_24_command_capability_negative_test.py",
        "wizard/tests/toybox_capability_matrix_test.py",
        "wizard/tests/toybox_adapter_lifecycle_test.py",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"capability matrix sign-off failed:\n{details}")
    print(proc.stdout.strip())
    print("[capability-matrix-signoff-v1.3.26] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
