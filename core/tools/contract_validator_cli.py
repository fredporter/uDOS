#!/usr/bin/env python3
"""
Contract Validator CLI (Core).

Runs validators in order:
  1) Vault Contract
  2) Theme Pack Contract
  3) LocId (World Contract)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.tools.contract_validator import (
    validate_theme_pack,
    validate_vault_contract,
    validate_world_contract,
)


def _print_report(name: str, report) -> int:
    print(f"[{name}] {'PASS' if report.valid else 'FAIL'}")
    for err in report.errors:
        print(f"  - {err}")
    for warn in report.warnings:
        print(f"  * {warn}")
    return 0 if report.valid else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate core contracts in order")
    parser.add_argument("--vault", default="vault", help="Path to vault root")
    parser.add_argument("--theme", default="themes/prose", help="Theme pack path")
    args = parser.parse_args(argv)

    failures = 0
    failures += _print_report("Vault Contract", validate_vault_contract(Path(args.vault)))
    failures += _print_report("Theme Pack Contract", validate_theme_pack(Path(args.theme)))
    failures += _print_report("LocId Contract", validate_world_contract(Path(args.vault)))

    return 0 if failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
