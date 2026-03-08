#!/usr/bin/env python3
"""v1.4.0 Sonic companion-repo CLI smoke gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SONIC_REPO = REPO.parent / "uDOS-sonic"
CLI = SONIC_REPO / "installers" / "usb" / "cli.py"


def main() -> int:
    if not CLI.exists():
        raise RuntimeError(f"external Sonic CLI not found: {CLI}")

    cmd = [sys.executable, str(CLI), "--help"]
    proc = subprocess.run(cmd, cwd=str(SONIC_REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"sonic CLI smoke failed:\n{details}")

    print(proc.stdout.strip())
    print("[sonic-docker-smoke-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
