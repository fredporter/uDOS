#!/usr/bin/env python3
"""Seed delivery manifest with a package entry."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: seed_cli.py <file_path> <name> <version>")
        return 1

    file_path = Path(sys.argv[1])
    name = sys.argv[2]
    version = sys.argv[3]

    if not file_path.exists():
        print("file not found")
        return 1

    repo_root = Path(__file__).resolve().parents[2]
    delivery_dir = repo_root / "memory" / "delivery"
    delivery_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = delivery_dir / "manifest.json"

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {
            "schema_version": "v1",
            "created_at": "",
            "packages": [],
        }

    entry = {
        "name": name,
        "version": version,
        "sha256": sha256_path(file_path),
        "size_bytes": file_path.stat().st_size,
        "url": str(file_path),
    }

    manifest["packages"].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print("seeded manifest entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
