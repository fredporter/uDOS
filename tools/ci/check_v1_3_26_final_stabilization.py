#!/usr/bin/env python3
"""v1.3.26 final stabilization pass for command/runtime surfaces."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List

REPO = Path(__file__).resolve().parents[2]


CHECK_COMMANDS: List[List[str]] = [
    [sys.executable, "tools/ci/check_v1_3_25_contract_freeze.py"],
    [sys.executable, "tools/ci/check_v1_3_23_contract_drift.py"],
    [sys.executable, "tools/ci/check_v1_3_24_world_state_migration_smoke.py"],
    [sys.executable, "tools/ci/check_v1_3_25_runtime_hardcoded_paths.py"],
    [sys.executable, "tools/ci/check_v1_3_25_long_run_soak.py", "--iterations", "600", "--ingest-batch", "128"],
]

TEST_COMMAND = [
    sys.executable,
    "-m",
    "pytest",
    "-q",
    "core/tests/gameplay_service_test.py",
    "core/tests/v1_3_24_command_capability_negative_test.py",
    "core/tests/v1_3_24_parity_reward_invariants_test.py",
]


def _run(cmd: List[str]) -> None:
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"check failed: {' '.join(cmd)}\n{details}")
    out = proc.stdout.strip()
    if out:
        print(out)


def main() -> int:
    for cmd in CHECK_COMMANDS:
        _run(cmd)
    _run(TEST_COMMAND)
    print("[final-stabilization-v1.3.26] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
