#!/usr/bin/env python3
"""Guardrail for Core TS dependency policy.

- Blocks heavy framework dependencies in `core/package.json`.
- Flags oversized transitive dependency graph from `core/package-lock.json`.
"""

from __future__ import annotations

import json
from pathlib import Path


BANNED = {
    "react",
    "react-dom",
    "next",
    "vue",
    "nuxt",
    "angular",
    "@angular/core",
    "svelte",
    "@sveltejs/kit",
    "electron",
}

MAX_TRANSITIVE = 120


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    pkg_path = repo / "core" / "package.json"
    lock_path = repo / "core" / "package-lock.json"

    if not pkg_path.exists():
        print("[core-ts-deps] SKIP: core/package.json missing.")
        return 0

    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    deps = set(pkg.get("dependencies", {}).keys())
    dev_deps = set(pkg.get("devDependencies", {}).keys())
    all_direct = deps | dev_deps

    banned_hits = sorted(BANNED.intersection(all_direct))
    if banned_hits:
        print("[core-ts-deps] FAIL: banned heavy deps present:")
        for dep in banned_hits:
            print(f"  - {dep}")
        return 1

    if not lock_path.exists():
        print("[core-ts-deps] FAIL: core/package-lock.json missing.")
        return 1

    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = lock.get("packages")
    if isinstance(packages, dict):
        # lockfile includes root package at key "".
        transitive_count = max(len(packages) - 1, 0)
    else:
        # Fallback for older lockfile shapes.
        transitive_count = len(lock.get("dependencies", {}))

    print(f"[core-ts-deps] transitive_count={transitive_count} max={MAX_TRANSITIVE}")
    if transitive_count > MAX_TRANSITIVE:
        print(
            "[core-ts-deps] FAIL: dependency graph too large for core runtime policy."
        )
        return 1

    print("[core-ts-deps] PASS: dependency policy check succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
