#!/usr/bin/env python3
"""v1.3.25 contract freeze gate for v1.3.x artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "tools" / "ci" / "baselines" / "v1_3_25_contract_freeze_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(manifest: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    rows = manifest.get("contracts")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("manifest has no contracts")

    missing: list[str] = []
    drift: list[dict[str, str]] = []
    checked_paths: list[str] = []

    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("manifest row is not an object")
        rel_path = str(row.get("path", "")).strip()
        expected = str(row.get("sha256", "")).strip().lower()
        if not rel_path or len(expected) != 64:
            raise RuntimeError(f"invalid manifest row: {row}")
        checked_paths.append(rel_path)

        full_path = repo_root / rel_path
        if not full_path.exists():
            missing.append(rel_path)
            continue
        actual = sha256_file(full_path)
        if actual != expected:
            drift.append({"path": rel_path, "expected": expected, "actual": actual})

    return {
        "ok": not missing and not drift,
        "checked": len(checked_paths),
        "checked_paths": checked_paths,
        "missing": missing,
        "drift": drift,
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing manifest: {path}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate v1.3.x frozen contract set")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to freeze manifest JSON")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = _load_manifest(manifest_path)
    report = verify_manifest(manifest, REPO)
    report["manifest"] = str(manifest_path.relative_to(REPO) if manifest_path.is_absolute() else manifest_path)

    print(json.dumps(report, indent=2))

    if not report["ok"]:
        raise RuntimeError("v1.3.25 contract freeze gate failed")

    print("[contract-freeze-v1.3.25] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
