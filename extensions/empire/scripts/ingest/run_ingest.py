#!/usr/bin/env python3
"""CLI entry for Empire ingestion.

Manual operator wrapper only.
Wizard Empire import routes and services are the canonical runtime surface.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from empire.services.ingestion_service import ingest_file, ingest_many


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest raw records to JSONL")
    parser.epilog = (
        "Operator wrapper only. Prefer Wizard Empire import actions for the supported runtime path."
    )
    parser.add_argument("inputs", nargs="+", help="Input files (.csv/.json/.jsonl)")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    parser.add_argument("--source", default=None, help="Optional source label")
    args = parser.parse_args()

    inputs = [Path(p) for p in args.inputs]
    out_path = Path(args.out)
    if len(inputs) == 1:
        count = ingest_file(inputs[0], out_path, source_label=args.source)
    else:
        count = ingest_many(inputs, out_path, source_label=args.source)
    print(f"Ingested {count} records -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
