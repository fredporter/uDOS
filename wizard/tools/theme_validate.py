#!/usr/bin/env python3
"""Theme pack validation CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from wizard.services.theme_validator import ThemePackValidator


def _print_report(results: Dict[str, object]) -> int:
    summary = results.get("summary") or {}
    total = summary.get("total", 0)
    invalid = summary.get("invalid", 0)
    valid = summary.get("valid", 0)

    print(f"Themes: {total} | Valid: {valid} | Invalid: {invalid}")
    for name, res in (results.get("results") or {}).items():
        status = "OK" if res.get("valid") else "FAIL"
        print(f"- {name}: {status}")
        for err in res.get("errors", []):
            print(f"  error: {err}")
        for warn in res.get("warnings", []):
            print(f"  warn: {warn}")

    return 0 if invalid == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate uDOS theme packs")
    parser.add_argument("--themes", default=None, help="Path to themes root")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    themes_root = Path(args.themes) if args.themes else None
    validator = ThemePackValidator(themes_root=themes_root)
    results = validator.validate_all()
    payload = {
        "summary": validator.summarize(results),
        "results": {
            name: {
                "valid": res.valid,
                "errors": res.errors,
                "warnings": res.warnings,
            }
            for name, res in results.items()
        },
    }

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0 if payload["summary"]["invalid"] == 0 else 1

    return _print_report(payload)


if __name__ == "__main__":
    raise SystemExit(main())
