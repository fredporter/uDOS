#!/usr/bin/env python3
"""Publish delivery manifest to a repo directory."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    delivery_dir = repo_root / "memory" / "delivery"
    manifest_path = delivery_dir / "manifest.json"
    repo_dir = repo_root / "distribution" / "delivery-repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    if not manifest_path.exists():
        print("manifest.json not found")
        return 1

    shutil.copy2(manifest_path, repo_dir / "manifest.json")
    print(f"published manifest to {repo_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
