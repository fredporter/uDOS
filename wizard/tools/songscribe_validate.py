#!/usr/bin/env python3
"""Songscribe validation CLI for uDOS."""

from __future__ import annotations

import json
from pathlib import Path

from library.songscribe.validate import validate_converters


def main() -> int:
    output_dir = Path("memory/groovebox/exports")
    result = validate_converters(output_dir)
    print(json.dumps(result, indent=2))
    return 0 if result.get("midi_exists") else 1


if __name__ == "__main__":
    raise SystemExit(main())
