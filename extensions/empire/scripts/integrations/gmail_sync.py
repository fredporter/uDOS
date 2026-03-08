#!/usr/bin/env python3
"""Sync Gmail contacts into Empire.

Manual operator wrapper only.
Wizard Empire connector routes and services are the canonical runtime surface.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from empire.integrations.google_gmail import fetch_and_ingest


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Gmail messages and ingest contacts")
    parser.epilog = (
        "Operator wrapper only. Prefer Wizard Empire connector actions for the supported runtime path."
    )
    parser.add_argument(
        "--credentials",
        default=None,
        help="Path to Google credentials.json (optional if stored in secret store)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Path to token.json (optional if stored in secret store)",
    )
    parser.add_argument("--query", default="", help="Gmail search query")
    parser.add_argument("--max", type=int, default=25, help="Max messages")
    parser.add_argument("--db", default=None, help="SQLite DB path")
    args = parser.parse_args()

    count = fetch_and_ingest(
        credentials_path=Path(args.credentials) if args.credentials else None,
        token_path=Path(args.token) if args.token else None,
        query=args.query,
        max_results=args.max,
        db_path=Path(args.db) if args.db else None,
    )
    print(f"Gmail ingested {count} contacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
