#!/usr/bin/env python3
"""Fetch Google Places and ingest into Empire.

Manual operator wrapper only.
Wizard Empire connector routes and services are the canonical runtime surface.
"""

from __future__ import annotations

import argparse

from empire.integrations.google_places import search_and_ingest


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Google Places and ingest records")
    parser.epilog = (
        "Operator wrapper only. Prefer Wizard Empire connector actions for the supported runtime path."
    )
    parser.add_argument("--api-key", default=None, help="Google Places API key")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--location", default="", help="Lat,lng")
    parser.add_argument("--radius", type=int, default=5000, help="Radius in meters")
    parser.add_argument("--db", default=None, help="SQLite DB path")
    args = parser.parse_args()

    count = search_and_ingest(
        api_key=args.api_key,
        query=args.query,
        location=args.location,
        radius_meters=args.radius,
        db_path=args.db,
    )
    print(f"Places ingested {count} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
