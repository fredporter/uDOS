#!/usr/bin/env python3
"""Mirror delivery repo to a target directory."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    source_dir = repo_root / "distribution" / "delivery-repo"

    if len(sys.argv) < 2:
        print("Usage: mirror_repo.py <target_dir>")
        return 1

    target_dir = Path(sys.argv[1])
    if not source_dir.exists():
        print("delivery-repo not found")
        return 1

    target_dir.mkdir(parents=True, exist_ok=True)
    for item in source_dir.iterdir():
        dest = target_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    print(f"mirrored to {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
