#!/usr/bin/env python3
"""
Songscribe setup helper.

This script scaffolds the Songscribe container directory and prints the
manual install steps for the ML stack. It is intentionally lightweight
so environments without Node/Python ML deps can still install the plugin
metadata without failing.
"""

from __future__ import annotations

from pathlib import Path

from wizard.services.path_utils import get_repo_root


def main() -> int:
    repo_root = get_repo_root()
    container_root = repo_root / "memory" / "library" / "containers" / "songscribe"
    container_root.mkdir(parents=True, exist_ok=True)

    print("Songscribe setup scaffolded.")
    print(f"Container directory: {container_root}")
    print("")
    print("Manual install steps (when ready):")
    print("  1) WIZARD CLONE songscribe")
    print("  2) pip install moseca basic-pitch adtof")
    print("  3) cd wizard/library/songscribe/repo")
    print("  4) npm install && npm run build")
    print("")
    print("Note: The ML transcription pipeline runs inside the Songscribe container.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
