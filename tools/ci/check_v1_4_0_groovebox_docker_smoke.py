#!/usr/bin/env python3
"""v1.4.0 Songscribe/Groovebox Dockerfile smoke gate."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCKERFILE = REPO / "library" / "songscribe" / "Dockerfile"


def main() -> int:
    if not DOCKERFILE.exists():
        raise RuntimeError("missing library/songscribe/Dockerfile")

    src = DOCKERFILE.read_text(encoding="utf-8")
    if "compileall" not in src:
        raise RuntimeError("songscribe Dockerfile missing compileall smoke step")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO)
    cmd = [sys.executable, "library/songscribe/validate.py"]
    proc = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        details = (proc.stdout + "\n" + proc.stderr).strip()
        raise RuntimeError(f"songscribe validate smoke failed:\n{details}")

    print(proc.stdout.strip())
    print("[groovebox-docker-smoke-v1.4.0] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
