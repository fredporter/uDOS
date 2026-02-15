#!/usr/bin/env python3
"""
Sonic Screwdriver setup helper.

Creates local runtime directories used by Sonic routes and flash-pack tooling.
"""

from __future__ import annotations

from wizard.services.path_utils import get_repo_root


def main() -> int:
    repo_root = get_repo_root()
    sonic_memory = repo_root / "memory" / "sonic"
    flash_pack_root = repo_root / "memory" / "sandbox" / "screwdriver" / "flash_packs"

    sonic_memory.mkdir(parents=True, exist_ok=True)
    flash_pack_root.mkdir(parents=True, exist_ok=True)

    print("Sonic Screwdriver setup complete.")
    print(f"Device DB location: {sonic_memory / 'sonic-devices.db'}")
    print(f"Flash packs path: {flash_pack_root}")
    print("Next: compile device DB if missing:")
    print("  sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
