#!/usr/bin/env python3
"""
Theme Pack Validator CLI (Core).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.tools.contract_validator import validate_theme_pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a uDOS theme pack")
    parser.add_argument("theme_dir", help="Path to theme pack directory")
    args = parser.parse_args(argv)

    report = validate_theme_pack(Path(args.theme_dir))
    if report.valid:
        print("Theme pack valid.")
        return 0

    print("Theme pack invalid.")
    for err in report.errors:
        print(f"- {err}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
