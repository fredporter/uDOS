#!/usr/bin/env python3
"""v1.4.0 Sonic Dockerfile smoke gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCKERFILE = REPO / "sonic" / "Dockerfile"


def main() -> int:
    src = DOCKERFILE.read_text(encoding="utf-8")
    if "core/sonic_cli.py" not in src:
        raise RuntimeError("sonic Dockerfile entrypoint is not wired to core/sonic_cli.py")

    cmd = [sys.executable, "sonic/core/sonic_cli.py", "--help"]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"sonic CLI smoke failed:\n{details}")

    print(proc.stdout.strip())
    print("[sonic-docker-smoke-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
