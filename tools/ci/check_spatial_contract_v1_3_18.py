#!/usr/bin/env python3
"""Validate v1.3.18 spatial LocId contract (optional -Z axis) across active runtimes."""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from core.services.anchor_validation import is_valid_locid
from core.tools.contract_validator import validate_world_contract


def _must_contain(path: Path, pattern: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not re.search(pattern, text):
        raise RuntimeError(f"{label} missing in {path}")


def _check_anchor_validation() -> None:
    valid = [
        "EARTH:SUR:L305-DA11",
        "EARTH:SUR:L305-DA11-Z0",
        "EARTH:SUB:L305-DA11-Z-9",
        "GAME:skyrim:SUB:L402-CC18-Z2",
    ]
    invalid = [
        "EARTH:SUR:L305-DA09",      # invalid row
        "EARTH:SUR:L305-DA11-Z100", # out-of-range z
        "EARTH:SUR:L305-DA11-Z",    # malformed z
    ]
    for token in valid:
        if not is_valid_locid(token):
            raise RuntimeError(f"anchor_validation rejected valid token: {token}")
    for token in invalid:
        if is_valid_locid(token):
            raise RuntimeError(f"anchor_validation accepted invalid token: {token}")


def _check_world_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="udos-spatial-v1-3-18-") as tmp:
        vault = Path(tmp)
        good = vault / "good.md"
        bad = vault / "bad.md"
        good.write_text(
            "\n".join(
                [
                    "---",
                    "places:",
                    "  - EARTH:SUR:L305-DA11-Z2",
                    "grid_locations:",
                    "  - L305-DA11-Z-2",
                    "---",
                ]
            ),
            encoding="utf-8",
        )
        bad.write_text("grid_locations: [L305-DA11-Z100]\n", encoding="utf-8")

        report = validate_world_contract(vault)
        if report.valid:
            raise RuntimeError("world contract unexpectedly valid with known invalid LocId")
        details = report.details or {}
        invalid = details.get("invalid_locids", [])
        if "L305-DA11-Z100" not in invalid:
            raise RuntimeError("world contract did not flag invalid z-axis LocId")

        bad.unlink()
        report_ok = validate_world_contract(vault)
        if not report_ok.valid:
            raise RuntimeError(f"world contract rejected valid z-axis LocIds: {report_ok.errors}")


def main() -> int:
    repo = REPO
    _must_contain(
        repo / "wizard" / "services" / "spatial_parser.py",
        r"LOCID_REGEX|(?:-Z\(-\?\\d\{1,2\}\)\?)",
        "wizard z-aware locid parser",
    )
    _must_contain(
        repo / "core" / "src" / "spatial" / "parse.ts",
        r"-Z\(-\?\\d\{1,2\}\)",
        "core ts z-aware locid parser",
    )
    _must_contain(
        repo / "core" / "src" / "spatial" / "schema.sql",
        r"L\{EffectiveLayer\}-\{FinalCell\}\[-Z\{z\}\]",
        "spatial schema z-axis contract comment",
    )
    _check_anchor_validation()
    _check_world_contract()
    print("[spatial-contract-v1.3.18] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
